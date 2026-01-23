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

### Option 1: Easy Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/DecentralizedJM/Mudrex-Trade-Ideas_Automation-SDK.git
cd Mudrex-Trade-Ideas_Automation-SDK

# Run the installation script
./install.sh
```

The script will:
- ✅ Check Python version (3.11+ required)
- ✅ Create virtual environment (optional)
- ✅ Install all dependencies including Mudrex Trading SDK
- ✅ Create configuration file from example

### Option 2: Using Makefile

```bash
git clone https://github.com/DecentralizedJM/Mudrex-Trade-Ideas_Automation-SDK.git
cd Mudrex-Trade-Ideas_Automation-SDK
make install
make setup
```

### Option 3: Manual Installation

```bash
# Install Mudrex Trading SDK first
pip install git+https://github.com/DecentralizedJM/mudrex-api-trading-python-sdk.git

# Install SDK dependencies
pip install -r requirements.txt

# Install the SDK
pip install -e .
```

### Setup (Interactive)

```bash
signal-sdk setup
```

**You'll be asked for:**
- 🔑 Mudrex API Secret (from Mudrex Settings → API Management)
  - ⚠️ **Important:** Copy the ENTIRE secret (usually 40+ characters)
  - ✅ The secret will be validated immediately to catch errors early
  - ✅ Make sure "Futures Trading" permission is enabled
- 💰 Trade Amount per signal (default: 50 USDT)
- ⚡ Maximum Leverage (default: 10x)
- 🌐 Broadcaster WebSocket URL

> **Important:** 
> - Your API key must have **"Futures Trading"** permission enabled
> - The setup will validate your API secret immediately - if it fails, check:
>   - You copied the entire secret (no missing characters)
>   - "Futures Trading" permission is enabled in Mudrex
>   - The secret hasn't been revoked or regenerated

### Start

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
- ✅ Configuration file exists and is valid
- ✅ Broadcaster WebSocket connection (validates actual connection)
- ✅ Mudrex API credentials (tests authentication)
- ✅ Detects placeholder URLs and provides guidance

> **Note:** The doctor command will attempt to connect to the broadcaster and validate your Mudrex API credentials. If you see placeholder URLs (like `your-broadcaster.railway.app`), update your `config.toml` with the actual broadcaster URL.

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
# If using virtual environment
source venv/bin/activate

# Update the SDK
pip install --upgrade git+https://github.com/DecentralizedJM/Mudrex-Trade-Ideas_Automation-SDK.git

# Or if installed in editable mode
cd Mudrex-Trade-Ideas_Automation-SDK
git pull
pip install -e .
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

---

## 🐳 Docker Support (Optional)

For users who prefer containerized deployments:

### Quick Start with Docker

```bash
# Build the image
docker build -t mudrex-signal-sdk .

# Create config directory
mkdir -p config logs

# Run setup (interactive)
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  mudrex-signal-sdk signal-sdk setup

# Start the SDK
docker run -d --name mudrex-signal-sdk \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  mudrex-signal-sdk
```

### Using Docker Compose

```bash
# Create config directory and add your config.toml
mkdir -p config logs

# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

> **Note:** Make sure to create `config/config.toml` before starting, or run `signal-sdk setup` interactively first.

---

## 📌 Version Pinning (Production)

For production deployments, it's recommended to pin the Mudrex Trading SDK to a specific version:

1. Check the latest stable commit/tag:
   ```bash
   git ls-remote --tags https://github.com/DecentralizedJM/mudrex-api-trading-python-sdk.git
   ```

2. Update `requirements.txt`:
   ```txt
   mudrex-api-trading-python-sdk @ git+https://github.com/DecentralizedJM/mudrex-api-trading-python-sdk.git@<commit-hash>
   ```

3. Reinstall:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

This prevents breaking changes from upstream updates.
