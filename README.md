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
- 🔑 Mudrex API Secret (from Mudrex Settings → API Management)
- 💰 Trade Amount per signal (default: 50 USDT)
- ⚡ Maximum Leverage (default: 10x)

> **Important:** Your API key must have **"Futures Trading"** permission enabled.

### 3. Start

```bash
signal-sdk start
```

**That's it!** You're now receiving and executing live signals.

---

## 📱 What You'll See

```
🚀 Mudrex Signal Automator v1.0.0
✅ Mudrex API: Valid! Balance: 500.00 USDT
✅ Connected to broadcaster

📡 Signal: LONG BTCUSDT
✅ Executed: Order placed LONG 0.001 @ 45000

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
| `signal-sdk test` | Test broadcaster connection |
| `signal-sdk doctor` | Diagnose all connectivity issues |

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
2. **SDK Receives** - Your SDK gets signal in real-time via WebSocket
3. **Validates** - Checks balance and safety limits
4. **Executes** - Places trade on your Mudrex account
5. **Manages** - Handles SL/TP, closes, updates automatically
6. **Logs** - Records everything for your review

---

## 🐛 Troubleshooting

### Run the Doctor

The easiest way to diagnose issues:

```bash
signal-sdk doctor
```

This checks:
- ✅ Configuration file
- ✅ Broadcaster connection
- ✅ Mudrex API credentials

### Common Errors

#### Error 401 - Invalid Credentials

```
❌ Invalid API credentials (401 Unauthorized)
```

**Fix:**
1. Double-check your API Secret from Mudrex
2. Ensure you're copying the **entire** secret
3. Try generating a new API key on Mudrex

#### Error 403 - Permission Denied

```
❌ API key lacks required permissions (403 Forbidden)
```

**Fix:**
1. Go to Mudrex → Settings → API Management
2. Edit your API key
3. Enable **"Futures Trading"** permission
4. Save and try again

#### Error 405 - Method Not Allowed

```
❌ API endpoint error (405 Method Not Allowed)
```

**Fix:**
- This is usually a temporary API issue
- Wait a few minutes and try again
- If persistent, contact support

#### Can't Connect to Broadcaster

```
❌ Connection failed
```

**Fix:**
1. Check your internet connection
2. Run `signal-sdk test` to verify
3. The service may be temporarily down - try again later

### Trades Not Executing

1. Check your configuration:
   ```bash
   signal-sdk status
   ```

2. Verify Mudrex account balance is sufficient

3. Review logs for errors:
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
- **Use Doctor** - Run `signal-sdk doctor` if anything seems wrong

---

## 📄 Support

For questions or issues, contact your signal provider or administrator.

---

**Ready to start?** Run `signal-sdk setup` and you'll be trading in 2 minutes! 🚀
