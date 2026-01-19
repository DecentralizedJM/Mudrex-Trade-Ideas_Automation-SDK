"""
Mudrex Signal Automator

Receive live trading signals and execute automatically on Mudrex.
"""

__version__ = "1.0.0"
__author__ = "Trade Ideas Automation Service"

from .client import SignalClient
from .executor import TradeExecutor
from .config import Config

__all__ = ["SignalClient", "TradeExecutor", "Config"]
