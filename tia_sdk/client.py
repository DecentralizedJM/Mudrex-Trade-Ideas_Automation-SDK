"""
WebSocket client for receiving signals from broadcaster.
"""

import asyncio
import json
import logging
import websockets
from typing import Optional, Callable, Awaitable
from datetime import datetime

from .config import Config
from .models import Signal, CloseCommand, EditSLTPCommand, LeverageCommand

logger = logging.getLogger(__name__)


class SignalClient:
    """WebSocket client for broadcaster connection."""
    
    def __init__(self, config: Config):
        self.config = config
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.reconnect_delay = 5
        self.max_reconnect_delay = 300  # 5 minutes
        
        # Callbacks
        self.on_signal: Optional[Callable[[Signal], Awaitable]] = None
        self.on_close: Optional[Callable[[CloseCommand], Awaitable]] = None
        self.on_edit_sltp: Optional[Callable[[EditSLTPCommand], Awaitable]] = None
        self.on_leverage: Optional[Callable[[LeverageCommand], Awaitable]] = None
        self.on_connected: Optional[Callable[[], Awaitable]] = None
        self.on_disconnected: Optional[Callable[[], Awaitable]] = None
    
    async def connect(self):
        """Connect to broadcaster WebSocket."""
        try:
            logger.info(f"Connecting to broadcaster: {self.config.broadcaster.url}")
            
            # Public service - no authentication required
            self.ws = await websockets.connect(
                self.config.broadcaster.url
            )
            
            logger.info("✅ Connected to broadcaster")
            
            if self.on_connected:
                await self.on_connected()
            
            # Reset reconnect delay on successful connection
            self.reconnect_delay = 5
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from broadcaster."""
        self.running = False
        if self.ws:
            await self.ws.close()
            self.ws = None
            logger.info("Disconnected from broadcaster")
    
    async def start(self):
        """Start receiving signals with auto-reconnection."""
        self.running = True
        
        while self.running:
            try:
                # Connect to broadcaster
                connected = await self.connect()
                
                if not connected:
                    logger.warning(f"Connection failed. Retrying in {self.reconnect_delay}s...")
                    await asyncio.sleep(self.reconnect_delay)
                    # Exponential backoff
                    self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
                    continue
                
                # Start ping task
                ping_task = asyncio.create_task(self._ping_loop())
                
                # Listen for messages
                try:
                    async for message in self.ws:
                        await self._handle_message(message)
                
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("Connection closed by server")
                
                finally:
                    ping_task.cancel()
                    
                    if self.on_disconnected:
                        await self.on_disconnected()
                
                # Reconnect if still running
                if self.running:
                    logger.info(f"Reconnecting in {self.reconnect_delay}s...")
                    await asyncio.sleep(self.reconnect_delay)
            
            except Exception as e:
                logger.error(f"Error in client loop: {e}", exc_info=True)
                await asyncio.sleep(self.reconnect_delay)
    
    async def _ping_loop(self):
        """Send periodic pings to keep connection alive."""
        try:
            while self.running and self.ws:
                await asyncio.sleep(30)
                if self.ws:
                    await self.ws.send("ping")
                    logger.debug("Sent ping")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in ping loop: {e}")
    
    async def _handle_message(self, message: str):
        """Handle incoming message from broadcaster."""
        try:
            # Handle pong response
            if message == "pong":
                logger.debug("Received pong")
                return
            
            # Parse JSON message
            data = json.loads(message)
            msg_type = data.get("type")
            
            logger.info(f"📨 Received: {msg_type}")
            
            # Route to appropriate handler
            if msg_type == "NEW_SIGNAL":
                await self._handle_new_signal(data)
            
            elif msg_type == "CLOSE_SIGNAL":
                await self._handle_close_signal(data)
            
            elif msg_type == "EDIT_SLTP":
                await self._handle_edit_sltp(data)
            
            elif msg_type == "UPDATE_LEVERAGE":
                await self._handle_leverage(data)
            
            else:
                logger.warning(f"Unknown message type: {msg_type}")
        
        except json.JSONDecodeError:
            logger.error(f"Failed to parse message: {message}")
        
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def _handle_new_signal(self, data: dict):
        """Handle NEW_SIGNAL message."""
        try:
            signal = Signal.from_dict(data["signal"])
            logger.info(f"📡 New Signal: {signal.signal_type.value} {signal.symbol} @ {signal.entry_price or 'Market'}")
            
            if self.on_signal:
                await self.on_signal(signal)
        
        except Exception as e:
            logger.error(f"Error handling new signal: {e}", exc_info=True)
    
    async def _handle_close_signal(self, data: dict):
        """Handle CLOSE_SIGNAL message."""
        try:
            close = CloseCommand(
                signal_id=data["signal_id"],
                symbol=data["symbol"],
                percentage=data.get("percentage", 100.0)
            )
            
            logger.info(f"🔒 Close Signal: {close.signal_id} ({close.percentage}%)")
            
            if self.on_close:
                await self.on_close(close)
        
        except Exception as e:
            logger.error(f"Error handling close signal: {e}", exc_info=True)
    
    async def _handle_edit_sltp(self, data: dict):
        """Handle EDIT_SLTP message."""
        try:
            edit = EditSLTPCommand(
                signal_id=data["signal_id"],
                symbol=data["symbol"],
                stop_loss=data.get("stop_loss"),
                take_profit=data.get("take_profit")
            )
            
            logger.info(f"✏️ Edit SL/TP: {edit.signal_id}")
            
            if self.on_edit_sltp:
                await self.on_edit_sltp(edit)
        
        except Exception as e:
            logger.error(f"Error handling edit SL/TP: {e}", exc_info=True)
    
    async def _handle_leverage(self, data: dict):
        """Handle UPDATE_LEVERAGE message."""
        try:
            lev = LeverageCommand(
                signal_id=data["signal_id"],
                symbol=data["symbol"],
                leverage=data["leverage"]
            )
            
            logger.info(f"⚡ Update Leverage: {lev.signal_id} → {lev.leverage}x")
            
            if self.on_leverage:
                await self.on_leverage(lev)
        
        except Exception as e:
            logger.error(f"Error handling leverage update: {e}", exc_info=True)
