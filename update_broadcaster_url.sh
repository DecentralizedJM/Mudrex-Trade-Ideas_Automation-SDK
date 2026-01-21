#!/bin/bash
#
# Update broadcaster URL in SDK after Railway deployment
#
# Usage: ./update_broadcaster_url.sh <your-railway-url>
# Example: ./update_broadcaster_url.sh tia-service-broadcaster-production.up.railway.app
#

if [ -z "$1" ]; then
    echo "❌ Error: Railway URL required"
    echo ""
    echo "Usage: ./update_broadcaster_url.sh <your-railway-url>"
    echo "Example: ./update_broadcaster_url.sh tia-service-broadcaster-production.up.railway.app"
    exit 1
fi

RAILWAY_URL="$1"
WEBSOCKET_URL="wss://${RAILWAY_URL}/ws"
API_SECRET="eeojo2WLw3b4TC65K6WQXwp84f8OBpzmeQWmYb2rQB4"

echo "📝 Updating SDK broadcaster configuration..."
echo ""
echo "Broadcaster URL: ${WEBSOCKET_URL}"
echo "API Secret: ${API_SECRET}"
echo ""

# Update constants.py
cat > tia_sdk/constants.py << EOF
"""
Constants - Broadcaster connection details (pre-configured).
"""

# Broadcaster connection (configured by service provider)
BROADCASTER_URL = "${WEBSOCKET_URL}"
BROADCASTER_API_SECRET = "${API_SECRET}"

# These are pre-configured and hidden from users
# Users only need to provide their Mudrex credentials
EOF

echo "✅ Updated tia_sdk/constants.py"
echo ""
echo "Next steps:"
echo "  1. git add tia_sdk/constants.py"
echo "  2. git commit -m 'Configure broadcaster URL for production'"
echo "  3. git push origin main"
echo ""
