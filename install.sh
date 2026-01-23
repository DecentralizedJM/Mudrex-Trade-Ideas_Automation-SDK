#!/bin/bash
# Mudrex Signal Automator SDK - Easy Installation Script
# This script handles all dependencies and installation steps

set -e  # Exit on error

echo "🚀 Mudrex Signal Automator SDK - Installation"
echo "=============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment (optional but recommended)
read -p "Create virtual environment? (recommended) [Y/n]: " create_venv
create_venv=${create_venv:-Y}

if [[ "$create_venv" =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
    echo "   To activate later: source venv/bin/activate"
    echo ""
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"
echo ""

# Install Mudrex Trading SDK first
echo "📥 Installing Mudrex Trading SDK..."
pip install git+https://github.com/DecentralizedJM/mudrex-api-trading-python-sdk.git
echo "✅ Mudrex Trading SDK installed"
echo ""

# Install SDK dependencies
echo "📥 Installing SDK dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Install SDK itself
echo "📥 Installing Signal Automator SDK..."
pip install -e .
echo "✅ Signal Automator SDK installed"
echo ""

# Create config from example
if [ ! -f "config.toml" ]; then
    echo "📝 Creating configuration file..."
    cp config.example.toml config.toml
    echo "✅ Configuration file created: config.toml"
    echo "   Please edit config.toml with your settings"
    echo ""
else
    echo "ℹ️  config.toml already exists, skipping..."
    echo ""
fi

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit config.toml with your Mudrex API credentials"
echo "  2. Run: signal-sdk setup  (interactive setup)"
echo "  3. Run: signal-sdk start  (start receiving signals)"
echo ""
if [[ "$create_venv" =~ ^[Yy]$ ]]; then
    echo "Remember to activate virtual environment:"
    echo "  source venv/bin/activate"
    echo ""
fi
