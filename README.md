# Mudrex Trade Ideas Automation SDK

**Receive live trading signals and execute automatically on Mudrex**

Install the SDK on your machine to receive real-time trade ideas and execute them directly on your Mudrex account. Your API keys stay on your machine - maximum security and control.

## 🎯 Why Use This SDK?

- ✅ **Real-time Signal Reception** - Get trade ideas as they're published
- ✅ **Automatic Execution** - Execute trades instantly on Mudrex
- ✅ **Your Keys, Your Control** - API keys never leave your machine
- ✅ **Risk Management** - Built-in safety limits and controls
- ✅ **Position Management** - Automatic SL/TP, closes, and updates
- ✅ **Simple Setup** - Install, configure, and start in minutes
- ✅ **Comprehensive Logging** - Track all signals and executions

## 🚀 Quick Start

### Installation

```bash
pip install tia-signal-automator
```

Or install from source:

```bash
git clone <repository-url>
cd Mudrex-Trade-Ideas_Automation-SDK
pip install -e .
```

### Setup

**1. Generate configuration file:**
```bash
tia-sdk init
```

**2. Edit your config** (`config.toml`):
```toml
[broadcaster]
url = "wss://your-signal-provider-url/ws"
api_secret = "your_access_secret"

[mudrex]
api_key = "your_mudrex_api_key"
api_secret = "your_mudrex_api_secret"

[trading]
enabled = true
trade_amount_usdt = 50.0
max_leverage = 10
```

**3. Start receiving signals:**
```bash
tia-sdk start
```

That's it! The SDK will now receive signals and execute trades automatically.

## 📋 Available Commands

```bash
tia-sdk init          # Generate configuration file
tia-sdk start         # Start receiving and executing signals
tia-sdk status        # Check your configuration
tia-sdk test          # Test connection to signal provider
tia-sdk history       # View trade execution history
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

### Risk Management Settings

```toml
[risk]
max_daily_trades = 20          # Max trades per day
max_open_positions = 5         # Max simultaneous positions
stop_on_daily_loss = 1000.0    # Stop if daily loss exceeds (USDT)
min_balance = 100.0            # Minimum balance required
```

### Logging Configuration

```toml
[logging]
level = "INFO"                 # DEBUG, INFO, WARNING, ERROR
file = "tia_sdk.log"           # Log file path
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
3. **Validates signal** and checks risk limits
4. **Executes trade** on your Mudrex account
5. **Sets SL/TP** automatically if provided
6. **Logs result** for your records

### Signal Types Handled

- **NEW_SIGNAL** - Opens new position with specified parameters
- **CLOSE_SIGNAL** - Closes position (full or partial)
- **EDIT_SLTP** - Updates stop loss and take profit
- **UPDATE_LEVERAGE** - Modifies position leverage

### Risk Protection

The SDK includes multiple safety features:

- ✅ Daily trade limits
- ✅ Maximum open positions limit
- ✅ Stop trading on daily loss threshold
- ✅ Minimum balance checks
- ✅ Leverage limits
- ✅ Position validation before execution

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
tia-sdk start
```

You'll see:
```
🚀 TIA Signal Automator SDK v1.0.0
✅ Connected to signal provider

📡 Signal: LONG BTCUSDT
✅ Executed: Order placed BUY 0.001 @ 45000

🔒 Close: BTCUSDT (100%)
✅ Position closed
```

### Check Configuration

```bash
tia-sdk status
```

Shows your current settings and validates configuration.

### Test Connection

```bash
tia-sdk test
```

Verifies connection to signal provider without starting trades.

## 🐛 Troubleshooting

### Connection Issues

**Problem:** Cannot connect to signal provider
- Verify `broadcaster.url` is correct
- Check `broadcaster.api_secret` is valid
- Ensure internet connection is stable
- Check firewall settings

**Test connection:**
```bash
tia-sdk test
```

### Trade Execution Issues

**Problem:** Trades not executing
- Verify Mudrex API credentials are correct
- Check you have sufficient balance
- Ensure `trading.enabled = true` in config
- Review logs for specific errors

**Check configuration:**
```bash
tia-sdk status
```

### View Logs

```bash
# Real-time log monitoring
tail -f tia_sdk.log

# Search for errors
grep ERROR tia_sdk.log

# View recent activity
tail -n 50 tia_sdk.log
```

## ⚙️ Advanced Configuration

### Multiple Instances

Run multiple SDK instances with different configs:

```bash
# Instance 1 - Conservative
tia-sdk start --config config_conservative.toml

# Instance 2 - Aggressive
tia-sdk start --config config_aggressive.toml
```

### Auto-start on System Boot

**Linux (systemd):**

Create `/etc/systemd/system/tia-sdk.service`:
```ini
[Unit]
Description=TIA Signal Automator SDK
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/sdk
ExecStart=/usr/local/bin/tia-sdk start
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable tia-sdk
sudo systemctl start tia-sdk
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
pip install --upgrade tia-signal-automator
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
4. **Set Appropriate Limits** - Configure risk limits for your strategy
5. **Regular Backups** - Backup your config and logs
6. **Update Regularly** - Keep SDK updated for latest features

## 📄 License

MIT License

## 👥 Support

For issues, questions, or feature requests, contact your signal provider or SDK administrator.

---

**Ready to start?** Run `tia-sdk init` to get started!
