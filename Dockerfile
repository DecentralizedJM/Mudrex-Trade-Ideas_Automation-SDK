# Mudrex Signal Automator SDK - Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Note: mudrex-api-trading-python-sdk is installed from git
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir git+https://github.com/DecentralizedJM/mudrex-api-trading-python-sdk.git && \
    pip install --no-cache-dir -r requirements.txt

# Copy SDK source code
COPY . .

# Install SDK in editable mode
RUN pip install --no-cache-dir -e .

# Create directory for config and logs
RUN mkdir -p /app/config /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CONFIG_PATH=/app/config/config.toml

# Volume for config and logs (persist across restarts)
VOLUME ["/app/config", "/app/logs"]

# Default command
CMD ["signal-sdk", "start"]
