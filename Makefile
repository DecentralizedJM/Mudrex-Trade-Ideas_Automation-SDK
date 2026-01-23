.PHONY: install setup test doctor help

help:
	@echo "Mudrex Signal Automator SDK - Makefile"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install all dependencies and SDK"
	@echo "  make setup      - Create config.toml from example"
	@echo "  make test       - Test broadcaster connection"
	@echo "  make doctor     - Run diagnostic checks"
	@echo "  make help       - Show this help message"
	@echo ""

install:
	@echo "🚀 Installing Mudrex Signal Automator SDK..."
	@python3 -m venv venv || true
	@. venv/bin/activate && \
		pip install --upgrade pip && \
		pip install git+https://github.com/DecentralizedJM/mudrex-api-trading-python-sdk.git && \
		pip install -r requirements.txt && \
		pip install -e .
	@echo "✅ Installation complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Activate virtual environment: source venv/bin/activate"
	@echo "  2. Run: make setup"
	@echo "  3. Edit config.toml with your credentials"
	@echo "  4. Run: signal-sdk start"

setup:
	@if [ ! -f "config.toml" ]; then \
		cp config.example.toml config.toml; \
		echo "✅ Configuration file created at config.toml"; \
		echo "   Please edit it with your Mudrex API credentials"; \
	else \
		echo "ℹ️  config.toml already exists"; \
	fi

test:
	@echo "🧪 Testing broadcaster connection..."
	@signal-sdk test || echo "❌ Test failed. Run 'signal-sdk doctor' for diagnostics."

doctor:
	@echo "🩺 Running diagnostics..."
	@signal-sdk doctor
