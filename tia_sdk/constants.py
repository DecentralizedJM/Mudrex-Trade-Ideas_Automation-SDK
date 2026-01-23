"""
Constants - Broadcaster connection details (default configuration).
"""

# Default Broadcaster WebSocket URL
# This is the production broadcaster URL - users can override in config.toml
# Format: wss://your-broadcaster.railway.app/ws
BROADCASTER_URL = "wss://tia-service-broadcaster-production.up.railway.app/ws"

# Note: Users can override this by:
# 1. Setting it in config.toml under [broadcaster].url
# 2. Setting BROADCASTER_URL environment variable
# 3. Providing it during 'signal-sdk setup' interactive setup
