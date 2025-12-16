# Use Python base image
FROM python:3.11-slim

# Install system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# The default_monitors.json will be copied via COPY command above
# No need to conditionally copy since it's now part of the repo

# Create data directory and ensure it's writable
# This ensures runtime data persists (if using Render disk, mount it here)
RUN mkdir -p /app/data && chmod 777 /app/data

# Make initialization script executable
RUN chmod +x /app/scripts/init_data.sh

# Expose port (Render will set PORT env var)
EXPOSE 8501

# Start command - initialize data then start Streamlit
CMD ["sh", "-c", "/app/scripts/init_data.sh && streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]

