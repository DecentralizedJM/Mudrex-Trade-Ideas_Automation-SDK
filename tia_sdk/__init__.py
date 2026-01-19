"""
TIA Signal Automator SDK

Local execution SDK for automated signal trading on Mudrex.
"""

__version__ = "1.0.0"
__author__ = "DecentralizedJM"

from .client import SignalClient
from .executor import TradeExecutor
from .config import Config

__all__ = ["SignalClient", "TradeExecutor", "Config"]
