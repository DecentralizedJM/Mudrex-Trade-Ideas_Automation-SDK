"""
Configuration management for SDK.
"""

import os
import toml
import uuid
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class BroadcasterConfig(BaseModel):
    """Broadcaster connection configuration."""
    url: str = Field(..., description="WebSocket URL of broadcaster")
    client_id: Optional[str] = Field(None, description="Unique client ID")
    telegram_id: Optional[int] = Field(None, description="Telegram ID for notifications")


class MudrexConfig(BaseModel):
    """Mudrex API configuration - only api_secret is required."""
    api_secret: str = Field(..., description="Mudrex API secret")


class TradingConfig(BaseModel):
    """Trading parameters."""
    enabled: bool = Field(True, description="Enable trade execution")
    trade_amount_usdt: float = Field(5.0, description="Trade amount per signal (minimum: 5.0 USDT)")
    max_leverage: int = Field(25, description="Maximum leverage")
    min_order_value: float = Field(5.0, description="Minimum order value (Mudrex requirement: 5.0 USDT)")
    auto_execute: bool = Field(True, description="Auto-execute trades")


class RiskConfig(BaseModel):
    """Risk management parameters (disabled by default)."""
    max_daily_trades: int = Field(999999, description="Max trades per day (disabled: 999999)")
    max_open_positions: int = Field(999999, description="Max open positions (disabled: 999999)")
    stop_on_daily_loss: float = Field(0.0, description="Stop on daily loss (0=disabled)")
    min_balance: float = Field(0.0, description="Minimum balance to trade (disabled: 0.0)")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field("INFO", description="Log level")
    file: str = Field("signal_sdk.log", description="Log file path")
    console: bool = Field(True, description="Log to console")
    rotate: bool = Field(True, description="Rotate log files")
    max_bytes: int = Field(10485760, description="Max log file size")
    backup_count: int = Field(5, description="Number of backup files")


class Config:
    """Main configuration class."""
    
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = Path(config_path)
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or environment."""
        if self.config_path.exists():
            # Load from TOML file
            data = toml.load(self.config_path)
            self._load_from_dict(data)
        else:
            # Load from environment variables
            self._load_from_env()
    
    def _load_from_dict(self, data: dict):
        """Load configuration from dictionary."""
        from .constants import BROADCASTER_URL
        
        # Generate client_id if not provided
        broadcaster_data = data.get("broadcaster", {})
        if "client_id" not in broadcaster_data or not broadcaster_data["client_id"]:
            broadcaster_data["client_id"] = f"sdk-{uuid.uuid4().hex[:8]}"
        
        # Use default broadcaster URL if not provided
        if "url" not in broadcaster_data or not broadcaster_data["url"]:
            broadcaster_data["url"] = BROADCASTER_URL
        
        self.broadcaster = BroadcasterConfig(**broadcaster_data)
        self.mudrex = MudrexConfig(**data.get("mudrex", {}))
        self.trading = TradingConfig(**data.get("trading", {}))
        self.risk = RiskConfig(**data.get("risk", {}))
        self.logging = LoggingConfig(**data.get("logging", {}))
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        from .constants import BROADCASTER_URL
        
        self.broadcaster = BroadcasterConfig(
            url=os.getenv("BROADCASTER_URL", BROADCASTER_URL),
            client_id=os.getenv("CLIENT_ID", f"sdk-{uuid.uuid4().hex[:8]}"),
            telegram_id=int(os.getenv("TELEGRAM_ID")) if os.getenv("TELEGRAM_ID") else None
        )
        
        self.mudrex = MudrexConfig(
            api_secret=os.getenv("MUDREX_API_SECRET", "")
        )
        
        self.trading = TradingConfig(
            enabled=os.getenv("TRADING_ENABLED", "true").lower() == "true",
            trade_amount_usdt=float(os.getenv("TRADE_AMOUNT", "5.0")),
            max_leverage=int(os.getenv("MAX_LEVERAGE", "25")),
            min_order_value=float(os.getenv("MIN_ORDER_VALUE", "5.0")),
            auto_execute=os.getenv("AUTO_EXECUTE", "true").lower() == "true"
        )
        
        self.risk = RiskConfig(
            max_daily_trades=999999,
            max_open_positions=999999,
            stop_on_daily_loss=0.0,
            min_balance=0.0
        )
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO")
        )
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # Broadcaster validation
        if not self.broadcaster.url:
            errors.append("Broadcaster URL is required")
        
        # Mudrex validation - only api_secret is required
        if not self.mudrex.api_secret:
            errors.append("Please enter your Mudrex API Secret in config.toml")
        elif self.mudrex.api_secret.strip() in ["your_mudrex_api_secret", "your-secret", "api_secret", ""]:
            errors.append("Please enter your actual Mudrex API Secret (not a placeholder)")
        
        # Trading validation
        if self.trading.trade_amount_usdt < self.trading.min_order_value:
            errors.append(f"Trade amount must be at least {self.trading.min_order_value} USDT (minimum required by Mudrex)")
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def generate_example(output_path: str = "config.example.toml"):
        """Generate example configuration file."""
        from .constants import BROADCASTER_URL
        
        example = {
            "broadcaster": {
                "url": BROADCASTER_URL,
                "client_id": "my-trading-bot-1",
                "telegram_id": 123456789
            },
            "mudrex": {
                "api_secret": "your_mudrex_api_secret"
            },
            "trading": {
                "enabled": True,
                "trade_amount_usdt": 5.0,
                "max_leverage": 25,
                "min_order_value": 5.0,
                "auto_execute": True
            },
            "risk": {
                "max_daily_trades": 999999,
                "max_open_positions": 999999,
                "stop_on_daily_loss": 0.0,
                "min_balance": 0.0
            },
            "logging": {
                "level": "INFO",
                "file": "signal_sdk.log",
                "console": True,
                "rotate": True,
                "max_bytes": 10485760,
                "backup_count": 5
            }
        }
        
        with open(output_path, "w") as f:
            toml.dump(example, f)
        
        return output_path
