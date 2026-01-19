# Mudrex Trade Ideas Automation SDK

**Local execution SDK for automated signal trading on Mudrex**

Connect to the centralized signal broadcaster and execute trades locally with your own API keys. Maximum security - your keys never leave your machine!

## 🎯 Features

- ✅ **Real-time Signal Reception** - WebSocket connection to broadcaster
- ✅ **Local Trade Execution** - Execute on your machine with your API keys
- ✅ **Automatic Position Management** - SL/TP updates, position closing
- ✅ **Risk Management** - Balance checks, max trades, safety limits
- ✅ **Auto-Reconnection** - Resilient to network issues
- ✅ **Comprehensive Logging** - Track all trades and signals
- ✅ **Simple Configuration** - TOML config file or environment variables

## 🚀 Quick Start

### Installation

```bash
pip install tia-signal-automator
```

### Setup

1. **Generate config:**
```bash
tia-sdk init
```

2. **Edit config file** (`config.toml`):
```toml
[broadcaster]
url = "wss://your-broadcaster.railway.app/ws"
api_secret = "your_api_secret"

[mudrex]
api_key = "your_mudrex_api_key"
api_secret = "your_mudrex_api_secret"

[trading]
enabled = true
trade_amount_usdt = 50.0
max_leverage = 10
```

3. **Start SDK:**
```bash
tia-sdk start
```

## 📋 Commands

```bash
tia-sdk init          # Generate config file
tia-sdk start         # Start receiving signals
tia-sdk status        # Check connection status
tia-sdk history       # View trade history
tia-sdk test          # Test connection
```

## 🔧 Configuration

### Config File (`config.toml`)

```toml
[broadcaster]
url = "wss://broadcaster.railway.app/ws"
api_secret = "shared_secret"
client_id = "my-unique-id"  # Auto-generated if not provided
telegram_id = 123456789     # Optional - for admin notifications

[mudrex]
api_key = "your_api_key"
api_secret = "your_api_secret"

[trading]
enabled = true
trade_amount_usdt = 50.0
max_leverage = 10
min_order_value = 8.0
auto_execute = true

[risk]
max_daily_trades = 20
max_open_positions = 5
stop_on_daily_loss = 1000.0

[logging]
level = "INFO"
file = "tia_sdk.log"
console = true
```

### Environment Variables

```bash
BROADCASTER_URL=wss://broadcaster.railway.app/ws
BROADCASTER_API_SECRET=your_secret
MUDREX_API_KEY=your_key
MUDREX_API_SECRET=your_secret
TRADE_AMOUNT=50.0
```

## 🏗️ Architecture

```
Broadcaster (Railway) → WebSocket → SDK (Your Machine) → Mudrex API
                                      ↓
                                 config.toml
                                 (API Keys)
```

**Your API keys never leave your machine!**

## 📊 Signal Handling

The SDK automatically handles:
- **NEW_SIGNAL** - Execute trade with configured amount
- **CLOSE_SIGNAL** - Close position (full or partial)
- **EDIT_SLTP** - Update stop loss / take profit
- **UPDATE_LEVERAGE** - Update position leverage

## 🔒 Security

- ✅ API keys stored locally (never sent to broadcaster)
- ✅ Encrypted config file support (optional)
- ✅ API secret authentication with broadcaster
- ✅ Secure WebSocket connection (WSS)
- ✅ Rate limiting and safety checks

## 📝 Example Trade Flow

1. Admin broadcasts signal via Telegram
2. Broadcaster sends signal via WebSocket
3. SDK receives signal → validates
4. SDK checks balance & risk limits
5. SDK executes trade via Mudrex API
6. SDK logs result & updates position tracking

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test connection
tia-sdk test

# Check logs
tail -f tia_sdk.log
```

### Trade Execution Issues
- Verify Mudrex API keys are correct
- Check balance in Mudrex account
- Ensure trading is enabled in config
- Review logs for specific errors

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [API Reference](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Related Projects

- [TIA Service Broadcaster](https://github.com/DecentralizedJM/TIA-Service-Broadcaster) - Signal broadcasting service

## 📄 License

MIT License

## 👥 Authors

- [@DecentralizedJM](https://github.com/DecentralizedJM)
