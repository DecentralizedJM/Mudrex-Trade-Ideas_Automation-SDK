"""
Data models for signals and trades.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SignalType(str, Enum):
    """Signal type enum."""
    LONG = "LONG"
    SHORT = "SHORT"


class OrderType(str, Enum):
    """Order type enum."""
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class SignalStatus(str, Enum):
    """Signal status enum."""
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


@dataclass
class Signal:
    """Trading signal received from broadcaster."""
    signal_id: str
    symbol: str
    signal_type: SignalType
    order_type: OrderType
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    leverage: int = 1
    status: SignalStatus = SignalStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Signal':
        """Create Signal from broadcaster message."""
        return cls(
            signal_id=data["signal_id"],
            symbol=data["symbol"],
            signal_type=SignalType(data["signal_type"]),
            order_type=OrderType(data["order_type"]),
            entry_price=data.get("entry_price"),
            stop_loss=data.get("stop_loss"),
            take_profit=data.get("take_profit"),
            leverage=data.get("leverage", 1),
            status=SignalStatus(data.get("status", "ACTIVE")),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )


@dataclass
class CloseCommand:
    """Position close command."""
    signal_id: str
    symbol: str
    percentage: float = 100.0


@dataclass
class EditSLTPCommand:
    """SL/TP edit command."""
    signal_id: str
    symbol: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class LeverageCommand:
    """Leverage update command."""
    signal_id: str
    symbol: str
    leverage: int


@dataclass
class TradeResult:
    """Result of trade execution."""
    signal_id: str
    symbol: str
    success: bool
    message: str
    order_id: Optional[str] = None
    executed_at: datetime = field(default_factory=datetime.utcnow)
    entry_price: Optional[float] = None
    quantity: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            "signal_id": self.signal_id,
            "symbol": self.symbol,
            "success": self.success,
            "message": self.message,
            "order_id": self.order_id,
            "executed_at": self.executed_at.isoformat(),
            "entry_price": self.entry_price,
            "quantity": self.quantity
        }
