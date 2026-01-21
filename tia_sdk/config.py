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
    """Mudrex API configuration."""
    api_key: str = Field(..., description="Mudrex API key")
    api_secret: str = Field(..., description="Mudrex API secret")


class TradingConfig(BaseModel):
    """Trading parameters."""
    enabled: bool = Field(True, description="Enable trade execution")
    trade_amount_usdt: float = Field(50.0, description="Trade amount per signal")
    max_leverage: int = Field(10, description="Maximum leverage")
    min_order_value: float = Field(8.0, description="Minimum order value")
    auto_execute: bool = Field(True, description="Auto-execute trades")


class RiskConfig(BaseModel):
    """Risk management parameters."""
    max_daily_trades: int = Field(20, description="Max trades per day")
    max_open_positions: int = Field(5, description="Max open positions")
    stop_on_daily_loss: float = Field(1000.0, description="Stop on daily loss (0=disabled)")
    min_balance: float = Field(100.0, description="Minimum balance to trade")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field("INFO", description="Log level")
    file: str = Field("tia_sdk.log", description="Log file path")
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
        # Generate client_id if not provided
        broadcaster_data = data.get("broadcaster", {})
        if "client_id" not in broadcaster_data or not broadcaster_data["client_id"]:
            broadcaster_data["client_id"] = f"sdk-{uuid.uuid4().hex[:8]}"
        
        self.broadcaster = BroadcasterConfig(**broadcaster_data)
        self.mudrex = MudrexConfig(**data.get("mudrex", {}))
        self.trading = TradingConfig(**data.get("trading", {}))
        self.risk = RiskConfig(**data.get("risk", {}))
        self.logging = LoggingConfig(**data.get("logging", {}))
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        self.broadcaster = BroadcasterConfig(
            url=os.getenv("BROADCASTER_URL", ""),
            client_id=os.getenv("CLIENT_ID", f"sdk-{uuid.uuid4().hex[:8]}"),
            telegram_id=int(os.getenv("TELEGRAM_ID")) if os.getenv("TELEGRAM_ID") else None
        )
        
        self.mudrex = MudrexConfig(
            api_key=os.getenv("MUDREX_API_KEY", ""),
            api_secret=os.getenv("MUDREX_API_SECRET", "")
        )
        
        self.trading = TradingConfig(
            enabled=os.getenv("TRADING_ENABLED", "true").lower() == "true",
            trade_amount_usdt=float(os.getenv("TRADE_AMOUNT", "50.0")),
            max_leverage=int(os.getenv("MAX_LEVERAGE", "10")),
            min_order_value=float(os.getenv("MIN_ORDER_VALUE", "8.0")),
            auto_execute=os.getenv("AUTO_EXECUTE", "true").lower() == "true"
        )
        
        self.risk = RiskConfig()
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
        
        # Mudrex validation
        if not self.mudrex.api_key:
            errors.append("Mudrex API key is required")
        if not self.mudrex.api_secret:
            errors.append("Mudrex API secret is required")
        
        # Trading validation
        if self.trading.trade_amount_usdt < self.trading.min_order_value:
            errors.append(f"Trade amount must be >= {self.trading.min_order_value}")
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def generate_example(output_path: str = "config.example.toml"):
        """Generate example configuration file."""
        example = {
            "broadcaster": {
                "url": "wss://your-broadcaster.railway.app/ws",
                "client_id": "my-trading-bot-1",
                "telegram_id": 123456789
            },
            "mudrex": {
                "api_key": "your_mudrex_api_key",
                "api_secret": "your_mudrex_api_secret"
            },
            "trading": {
                "enabled": True,
                "trade_amount_usdt": 50.0,
                "max_leverage": 10,
                "min_order_value": 8.0,
                "auto_execute": True
            },
            "risk": {
                "max_daily_trades": 20,
                "max_open_positions": 5,
                "stop_on_daily_loss": 1000.0,
                "min_balance": 100.0
            },
            "logging": {
                "level": "INFO",
                "file": "tia_sdk.log",
                "console": True,
                "rotate": True,
                "max_bytes": 10485760,
                "backup_count": 5
            }
        }
        
        with open(output_path, "w") as f:
            toml.dump(example, f)
        
        return output_path
