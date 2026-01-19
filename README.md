# Mudrex Signal Automator

**Receive live trading signals and execute automatically on Mudrex**

Professional signal execution SDK that runs on your machine. Your API keys stay secure and local - never shared with anyone.

## 🎯 Benefits

- ✅ **Real-time Signal Execution** - Execute trades as signals arrive
- ✅ **Your Keys, Your Control** - API keys never leave your machine
- ✅ **Automatic Management** - SL/TP updates, position closes handled automatically
- ✅ **2-Minute Setup** - Simple installation and configuration
- ✅ **Professional Logging** - Complete trade history and audit trail

---

## 🚀 Quick Start

### 1. Install

```bash
pip install git+https://github.com/DecentralizedJM/Mudrex-Trade-Ideas_Automation-SDK.git
```

### 2. Setup (Interactive)

```bash
signal-sdk setup
```

**You'll be asked for:**
- 🔑 Mudrex API Key
- 🔑 Mudrex API Secret  
- 💰 Trade Amount per signal (default: 50 USDT)
- ⚡ Maximum Leverage (default: 10x)

### 3. Start

```bash
signal-sdk start
```

**That's it!** You're now receiving and executing live signals.

---

## 📱 What You'll See

```
🚀 Mudrex Signal Automator v1.0.0
✅ Connected to signal provider

📡 Signal: LONG BTCUSDT
✅ Executed: Order placed BUY 0.001 @ 45000

📡 Signal: EDIT_SLTP BTCUSDT
✅ SL/TP updated

🔒 Close: BTCUSDT
✅ Position closed
```

---

## 📋 Commands

| Command | Description |
|---------|-------------|
| `signal-sdk setup` | Interactive configuration (start here!) |
| `signal-sdk start` | Start receiving signals |
| `signal-sdk status` | Check your configuration |
| `signal-sdk test` | Test connection |

---

## 🔒 Security

### Your API Keys Are Safe

- ✅ Stored **only on your machine**
- ✅ Never transmitted to signal provider
- ✅ Only used for **your** Mudrex trades
- ✅ Full control over your account

### Keep Your Config Secure

- Store `config.toml` safely
- Never share your configuration file
- Back up your config regularly

---

## 🔧 Configuration

After running `signal-sdk setup`, your `config.toml` will be created with:

```toml
[mudrex]
api_key = "your_key"
api_secret = "your_secret"

[trading]
trade_amount_usdt = 50.0    # Amount per trade
max_leverage = 10            # Maximum leverage
auto_execute = true          # Execute automatically
```

You can edit these values anytime by opening `config.toml`.

---

## 📊 How It Works

1. **Signal Arrives** - New trading signal published
2. **SDK Receives** - Your SDK gets signal in real-time
3. **Validates** - Checks balance and safety limits
4. **Executes** - Places trade on your Mudrex account
5. **Manages** - Handles SL/TP, closes, updates automatically
6. **Logs** - Records everything for your review

---

## 🐛 Troubleshooting

### Can't Connect

```bash
signal-sdk test
```

Check that your internet connection is stable.

### Trades Not Executing

1. Verify Mudrex API credentials:
   ```bash
   signal-sdk status
   ```

2. Check Mudrex account balance

3. Review logs:
   ```bash
   tail -f signal_sdk.log
   ```

### Update Configuration

Edit your settings:
```bash
nano config.toml
```

Or run setup again:
```bash
signal-sdk setup
```

---

## 🔄 Updates

Keep your SDK updated:

```bash
pip install --upgrade git+https://github.com/DecentralizedJM/Mudrex-Trade-Ideas_Automation-SDK.git
```

---

## 💡 Tips

- **Start Small** - Begin with smaller trade amounts to test
- **Monitor Logs** - Check `signal_sdk.log` regularly
- **Keep Funded** - Maintain adequate balance in Mudrex
- **Backup Config** - Save your `config.toml` securely

---

## 📄 Support

For questions or issues, contact your signal provider or administrator.

---

**Ready to start?** Run `signal-sdk setup` and you'll be trading in 2 minutes! 🚀
