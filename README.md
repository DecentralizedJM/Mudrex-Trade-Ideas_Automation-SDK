# Mudrex Signal Automator

**Receive live trading signals and execute automatically on Mudrex**

Install the SDK on your machine to receive real-time trade ideas and execute them directly on your Mudrex account. Your API keys stay on your machine - maximum security and control.

## 🎯 Why Use This SDK?

- ✅ **Real-time Signal Reception** - Get trade ideas as they're published
- ✅ **Automatic Execution** - Execute trades instantly on Mudrex
- ✅ **Your Keys, Your Control** - API keys never leave your machine
- ✅ **Position Management** - Automatic SL/TP, closes, and updates
- ✅ **Simple Setup** - Install, configure, and start in minutes
- ✅ **Comprehensive Logging** - Track all signals and executions

## 🚀 Quick Start

### Installation

```bash
pip install git+https://github.com/DecentralizedJM/Mudrex-Trade-Ideas_Automation-SDK.git
```

### Interactive Setup (Recommended)

**Just answer a few questions and you're ready!**

```bash
signal-sdk setup
```

**You'll be asked for:**
- 🔑 Your Mudrex API Key
- 🔑 Your Mudrex API Secret
- 💰 Trade Amount (default: 50 USDT)
- ⚡ Max Leverage (default: 10x)
- 📱 Telegram ID (optional, for notifications)

**That's it!** The SDK is automatically configured and ready.

### Start Receiving Signals

```bash
signal-sdk start
```

You'll see:
```
🚀 Mudrex Signal Automator v1.0.0
✅ Connected to signal provider

📡 Signal: LONG BTCUSDT
✅ Executed: Order placed BUY 0.001 @ 45000
```

## 📋 Available Commands

```bash
signal-sdk setup         # Interactive setup (easiest!)
signal-sdk start         # Start receiving and executing signals
signal-sdk status        # Check your configuration
signal-sdk test          # Test connection
signal-sdk init          # Generate config file (advanced)
signal-sdk history       # View trade history (coming soon)
```

## 🔧 Configuration

### Basic Configuration

Create a `config.toml` file with your settings:

```toml
[broadcaster]
# Signal provider connection
url = "wss://signal-provider/ws"
api_secret = "your_access_secret"
client_id = "my-trading-bot"  # Auto-generated if not provided

[mudrex]
# Your Mudrex API credentials
api_key = "your_api_key"
api_secret = "your_api_secret"

[trading]
# Trading parameters
enabled = true
trade_amount_usdt = 50.0     # Amount per trade in USDT
max_leverage = 10             # Maximum leverage to use
auto_execute = true           # Execute automatically
```

### Logging Configuration

```toml
[logging]
level = "INFO"                 # DEBUG, INFO, WARNING, ERROR
file = "signal_sdk.log"        # Log file path
console = true                 # Also print to console
rotate = true                  # Rotate log files
```

### Environment Variables

You can also use environment variables:

```bash
BROADCASTER_URL=wss://signal-provider/ws
BROADCASTER_API_SECRET=your_secret
MUDREX_API_KEY=your_key
MUDREX_API_SECRET=your_secret
TRADE_AMOUNT=50.0
MAX_LEVERAGE=10
```

## 📊 How It Works

### Signal Reception & Execution

1. **SDK connects** to the signal provider via secure WebSocket
2. **Receives signals** in real-time as they're published
3. **Validates signal** and checks safety limits
4. **Executes trade** on your Mudrex account
5. **Sets SL/TP** automatically if provided
6. **Logs result** for your records

### Signal Types Handled

- **NEW_SIGNAL** - Opens new position with specified parameters
- **CLOSE_SIGNAL** - Closes position (full or partial)
- **EDIT_SLTP** - Updates stop loss and take profit
- **UPDATE_LEVERAGE** - Modifies position leverage

## 🔒 Security

### Your API Keys Stay Local

- API keys are stored only on your machine
- Keys are never transmitted to the signal provider
- Only trade execution happens via Mudrex API
- Full control over your funds at all times

### Configuration Security

- Store `config.toml` securely on your machine
- Never share your configuration file
- Use `.gitignore` to prevent accidental commits
- Consider encrypting sensitive config files

## 📝 Example Usage

### Start in Foreground (see output)

```bash
signal-sdk start
```

You'll see:
```
🚀 Mudrex Signal Automator v1.0.0
✅ Connected to signal provider

📡 Signal: LONG BTCUSDT
✅ Executed: Order placed BUY 0.001 @ 45000

🔒 Close: BTCUSDT (100%)
✅ Position closed
```

### Check Configuration

```bash
signal-sdk status
```

Shows your current settings and validates configuration.

### Test Connection

```bash
signal-sdk test
```

Verifies connection to signal provider without starting trades.

## 🐛 Troubleshooting

### Connection Issues

**Problem:** Cannot connect to signal provider
- Verify `url` is correct in config
- Check `api_secret` is valid
- Ensure internet connection is stable
- Check firewall settings

**Test connection:**
```bash
signal-sdk test
```

### Trade Execution Issues

**Problem:** Trades not executing
- Verify Mudrex API credentials are correct
- Check you have sufficient balance
- Ensure `trading.enabled = true` in config
- Review logs for specific errors

**Check configuration:**
```bash
signal-sdk status
```

### View Logs

```bash
# Real-time log monitoring
tail -f signal_sdk.log

# Search for errors
grep ERROR signal_sdk.log

# View recent activity
tail -n 50 signal_sdk.log
```

## ⚙️ Advanced Configuration

### Multiple Instances

Run multiple SDK instances with different configs:

```bash
# Instance 1 - Conservative
signal-sdk start --config config_conservative.toml

# Instance 2 - Aggressive
signal-sdk start --config config_aggressive.toml
```

### Auto-start on System Boot

**Linux (systemd):**

Create `/etc/systemd/system/signal-sdk.service`:
```ini
[Unit]
Description=Mudrex Signal Automator
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/sdk
ExecStart=/usr/local/bin/signal-sdk start
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable signal-sdk
sudo systemctl start signal-sdk
```

## 📊 Performance & Reliability

- **Auto-reconnection** - Reconnects automatically if connection drops
- **Heartbeat monitoring** - Maintains connection health
- **Exponential backoff** - Smart retry on connection failures
- **Transaction logging** - Complete audit trail of all trades
- **Error recovery** - Graceful handling of API errors

## 🔄 Updates

Keep your SDK up to date:

```bash
pip install --upgrade mudrex-signal-automator
```

Or from source:
```bash
cd Mudrex-Trade-Ideas_Automation-SDK
git pull
pip install -e .
```

## 💡 Best Practices

1. **Start Small** - Begin with small trade amounts to test
2. **Monitor Logs** - Regularly check logs for issues
3. **Keep Balance Funded** - Maintain adequate balance for trades
4. **Set Appropriate Limits** - Configure limits for your strategy
5. **Regular Backups** - Backup your config and logs
6. **Update Regularly** - Keep SDK updated for latest features

## 📄 License

MIT License

## 👥 Support

For issues, questions, or feature requests, contact your signal provider or SDK administrator.

---

**Ready to start?** Run `signal-sdk init` to get started!
