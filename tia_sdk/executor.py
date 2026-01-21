"""
Trade executor - executes trades on Mudrex using local API keys.
"""

import logging
import asyncio
from typing import Optional
from datetime import datetime, timedelta
from mudrex import MudrexClient

from .config import Config
from .models import (
    Signal, CloseCommand, EditSLTPCommand, LeverageCommand,
    TradeResult, SignalType, OrderType
)

logger = logging.getLogger(__name__)


class TradeExecutor:
    """Executes trades on Mudrex based on signals."""
    
    def __init__(self, config: Config):
        self.config = config
        # MudrexClient only takes api_secret (not api_key)
        self.client = MudrexClient(
            api_secret=config.mudrex.api_secret
        )
        
        # Track state
        self.daily_trades = 0
        self.daily_loss = 0.0
        self.last_reset = datetime.now().date()
        self.open_positions: dict[str, Signal] = {}  # signal_id -> Signal
        
        logger.info("TradeExecutor initialized")
    
    def _reset_daily_counters(self):
        """Reset daily counters if new day."""
        today = datetime.now().date()
        if today != self.last_reset:
            self.daily_trades = 0
            self.daily_loss = 0.0
            self.last_reset = today
            logger.info("Daily counters reset")
    
    async def _check_risk_limits(self) -> tuple[bool, str]:
        """
        Check if risk limits allow trading.
        
        Returns:
            (can_trade, reason)
        """
        self._reset_daily_counters()
        
        # Check if trading is enabled
        if not self.config.trading.enabled:
            return False, "Trading is disabled in config"
        
        # Check daily trade limit
        if self.daily_trades >= self.config.risk.max_daily_trades:
            return False, f"Daily trade limit reached ({self.config.risk.max_daily_trades})"
        
        # Check open positions limit
        if len(self.open_positions) >= self.config.risk.max_open_positions:
            return False, f"Max open positions reached ({self.config.risk.max_open_positions})"
        
        # Check daily loss limit
        if self.config.risk.stop_on_daily_loss > 0 and self.daily_loss >= self.config.risk.stop_on_daily_loss:
            return False, f"Daily loss limit reached ({self.daily_loss:.2f} USDT)"
        
        # Check balance using wallet.get_futures_balance()
        try:
            balance = await asyncio.to_thread(self.client.wallet.get_futures_balance)
            available_balance = float(balance.available_balance)
            
            if available_balance < self.config.risk.min_balance:
                return False, f"Balance too low ({available_balance:.2f} < {self.config.risk.min_balance} USDT)"
        
        except Exception as e:
            logger.error(f"Failed to check balance: {e}")
            return False, f"Failed to check balance: {str(e)}"
        
        return True, "OK"
    
    async def execute_signal(self, signal: Signal) -> TradeResult:
        """
        Execute a new trading signal.
        
        Returns:
            TradeResult with execution details
        """
        logger.info(f"🎯 Executing signal: {signal.signal_type.value} {signal.symbol}")
        
        # Check if auto-execute is enabled
        if not self.config.trading.auto_execute:
            logger.info("Auto-execute disabled - signal logged but not executed")
            return TradeResult(
                signal_id=signal.signal_id,
                symbol=signal.symbol,
                success=False,
                message="Auto-execute disabled"
            )
        
        # Check risk limits
        can_trade, reason = await self._check_risk_limits()
        if not can_trade:
            logger.warning(f"Risk limit check failed: {reason}")
            return TradeResult(
                signal_id=signal.signal_id,
                symbol=signal.symbol,
                success=False,
                message=f"Risk limit: {reason}"
            )
        
        try:
            # Check if position already exists
            positions = await asyncio.to_thread(self.client.positions.list_open)
            existing = next((p for p in positions if p.symbol == signal.symbol), None)
            
            if existing:
                logger.warning(f"Position already exists for {signal.symbol}")
                return TradeResult(
                    signal_id=signal.signal_id,
                    symbol=signal.symbol,
                    success=False,
                    message=f"Position already exists for {signal.symbol}"
                )
            
            # Get asset info
            asset = await asyncio.to_thread(self.client.assets.get, signal.symbol)
            if not asset:
                return TradeResult(
                    signal_id=signal.signal_id,
                    symbol=signal.symbol,
                    success=False,
                    message=f"Asset {signal.symbol} not found"
                )
            
            # Calculate quantity
            trade_amount = self.config.trading.trade_amount_usdt
            entry_price = signal.entry_price if signal.order_type == OrderType.LIMIT else float(asset.mark_price)
            
            # Use min leverage between signal and config
            leverage = min(signal.leverage, self.config.trading.max_leverage)
            
            # Calculate quantity
            quantity = (trade_amount * leverage) / entry_price
            
            # Round to quantity step
            if asset.quantity_step:
                qty_step = float(asset.quantity_step)
                quantity = round(quantity / qty_step) * qty_step
            
            # Format quantity
            if asset.quantity_step and float(asset.quantity_step) < 1:
                precision = len(str(float(asset.quantity_step)).split('.')[-1].rstrip('0'))
                quantity_str = f"{quantity:.{precision}f}"
            else:
                quantity_str = str(int(quantity))
            
            # Determine side - use string value, not Enum
            side = "LONG" if signal.signal_type == SignalType.LONG else "SHORT"
            
            # Place order using correct method names
            if signal.order_type == OrderType.MARKET:
                order = await asyncio.to_thread(
                    self.client.orders.create_market_order,
                    symbol=signal.symbol,
                    side=side,
                    quantity=quantity_str,
                    leverage=leverage
                )
            else:
                order = await asyncio.to_thread(
                    self.client.orders.create_limit_order,
                    symbol=signal.symbol,
                    side=side,
                    quantity=quantity_str,
                    price=str(signal.entry_price),
                    leverage=leverage
                )
            
            # Set SL/TP if provided
            if signal.stop_loss or signal.take_profit:
                # Wait a moment for position to be created
                await asyncio.sleep(2)
                
                positions = await asyncio.to_thread(self.client.positions.list_open)
                position = next((p for p in positions if p.symbol == signal.symbol), None)
                
                if position:
                    sl_price = str(signal.stop_loss) if signal.stop_loss else None
                    tp_price = str(signal.take_profit) if signal.take_profit else None
                    
                    await asyncio.to_thread(
                        self.client.positions.set_risk_order,
                        position_id=position.position_id,
                        stoploss_price=sl_price,
                        takeprofit_price=tp_price
                    )
                    
                    logger.info(f"Set SL/TP for {signal.symbol}: SL={sl_price}, TP={tp_price}")
            
            # Track position
            self.open_positions[signal.signal_id] = signal
            self.daily_trades += 1
            
            logger.info(f"✅ Trade executed: {signal.symbol} {side} {quantity_str} @ {entry_price}")
            
            return TradeResult(
                signal_id=signal.signal_id,
                symbol=signal.symbol,
                success=True,
                message=f"Order placed: {side} {quantity_str} @ {entry_price}",
                order_id=order.order_id if hasattr(order, 'order_id') else None,
                entry_price=entry_price,
                quantity=quantity
            )
        
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}", exc_info=True)
            return TradeResult(
                signal_id=signal.signal_id,
                symbol=signal.symbol,
                success=False,
                message=f"Execution error: {str(e)}"
            )
    
    async def close_position(self, close: CloseCommand) -> TradeResult:
        """Close a position (full or partial)."""
        logger.info(f"🔒 Closing position: {close.symbol} ({close.percentage}%)")
        
        try:
            # Find position
            positions = await asyncio.to_thread(self.client.positions.list_open)
            position = next((p for p in positions if p.symbol == close.symbol), None)
            
            if not position:
                return TradeResult(
                    signal_id=close.signal_id,
                    symbol=close.symbol,
                    success=False,
                    message=f"No open position for {close.symbol}"
                )
            
            # Close position
            if close.percentage >= 100:
                # Full close
                result = await asyncio.to_thread(
                    self.client.positions.close,
                    position.position_id
                )
                logger.info(f"✅ Position closed: {close.symbol}")
            else:
                # Partial close
                close_qty = float(position.quantity) * (close.percentage / 100.0)
                
                # Round to quantity step
                asset = await asyncio.to_thread(self.client.assets.get, close.symbol)
                if asset and asset.quantity_step:
                    qty_step = float(asset.quantity_step)
                    close_qty = round(close_qty / qty_step) * qty_step
                    
                    if float(asset.quantity_step) < 1:
                        precision = len(str(float(asset.quantity_step)).split('.')[-1].rstrip('0'))
                        close_qty_str = f"{close_qty:.{precision}f}"
                    else:
                        close_qty_str = str(int(close_qty))
                else:
                    close_qty_str = str(close_qty)
                
                result = await asyncio.to_thread(
                    self.client.positions.close_partial,
                    position.position_id,
                    close_qty_str
                )
                logger.info(f"✅ Position partially closed: {close.symbol} ({close.percentage}%)")
            
            # Remove from tracking if fully closed
            if close.percentage >= 100 and close.signal_id in self.open_positions:
                del self.open_positions[close.signal_id]
            
            return TradeResult(
                signal_id=close.signal_id,
                symbol=close.symbol,
                success=True,
                message=f"Position closed ({close.percentage}%)"
            )
        
        except Exception as e:
            logger.error(f"Failed to close position: {e}", exc_info=True)
            return TradeResult(
                signal_id=close.signal_id,
                symbol=close.symbol,
                success=False,
                message=f"Close error: {str(e)}"
            )
    
    async def update_sl_tp(self, edit: EditSLTPCommand) -> TradeResult:
        """Update SL/TP for a position."""
        logger.info(f"✏️ Updating SL/TP: {edit.symbol}")
        
        try:
            # Find position
            positions = await asyncio.to_thread(self.client.positions.list_open)
            position = next((p for p in positions if p.symbol == edit.symbol), None)
            
            if not position:
                return TradeResult(
                    signal_id=edit.signal_id,
                    symbol=edit.symbol,
                    success=False,
                    message=f"No open position for {edit.symbol}"
                )
            
            # Update SL/TP
            sl_price = str(edit.stop_loss) if edit.stop_loss else None
            tp_price = str(edit.take_profit) if edit.take_profit else None
            
            await asyncio.to_thread(
                self.client.positions.set_risk_order,
                position_id=position.position_id,
                stoploss_price=sl_price,
                takeprofit_price=tp_price
            )
            
            logger.info(f"✅ SL/TP updated: {edit.symbol}")
            
            return TradeResult(
                signal_id=edit.signal_id,
                symbol=edit.symbol,
                success=True,
                message=f"SL/TP updated: SL={sl_price}, TP={tp_price}"
            )
        
        except Exception as e:
            logger.error(f"Failed to update SL/TP: {e}", exc_info=True)
            return TradeResult(
                signal_id=edit.signal_id,
                symbol=edit.symbol,
                success=False,
                message=f"Update error: {str(e)}"
            )
    
    async def update_leverage(self, lev: LeverageCommand) -> TradeResult:
        """Update leverage for a position."""
        logger.info(f"⚡ Updating leverage: {lev.symbol} → {lev.leverage}x")
        
        try:
            # Find position
            positions = await asyncio.to_thread(self.client.positions.list_open)
            position = next((p for p in positions if p.symbol == lev.symbol), None)
            
            if not position:
                return TradeResult(
                    signal_id=lev.signal_id,
                    symbol=lev.symbol,
                    success=False,
                    message=f"No open position for {lev.symbol}"
                )
            
            # Update leverage (via Mudrex SDK if supported)
            # Note: Check if Mudrex SDK has leverage update method
            logger.warning("Leverage update not yet implemented in Mudrex SDK")
            
            return TradeResult(
                signal_id=lev.signal_id,
                symbol=lev.symbol,
                success=False,
                message="Leverage update not supported yet"
            )
        
        except Exception as e:
            logger.error(f"Failed to update leverage: {e}", exc_info=True)
            return TradeResult(
                signal_id=lev.signal_id,
                symbol=lev.symbol,
                success=False,
                message=f"Leverage error: {str(e)}"
            )
    
    async def validate_credentials(self) -> tuple[bool, str]:
        """
        Validate Mudrex API credentials by making a test API call.
        
        Returns:
            (valid, message)
        """
        try:
            balance = await asyncio.to_thread(self.client.wallet.get_futures_balance)
            available = float(balance.available_balance)
            return True, f"Valid! Balance: {available:.2f} USDT"
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg.lower():
                return False, "Invalid API credentials (401 Unauthorized)"
            elif "403" in error_msg or "Forbidden" in error_msg.lower():
                return False, "API key lacks required permissions (403 Forbidden)"
            elif "405" in error_msg:
                return False, "API endpoint error (405 Method Not Allowed)"
            else:
                return False, f"API error: {error_msg}"
