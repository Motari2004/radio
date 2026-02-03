# Base image with Python 3.11 (compatible with greenlet)
FROM python:3.11-slim

# Install necessary system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    libnss3 \
    libatk1.0-0 \
    libcups2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    ca-certificates \
    fonts-liberation \
    unzip \
    xvfb \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt bot.py ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

# Expose port for screenshot endpoint
EXPOSE 10000

# Start the bot
CMD ["python", "bot.py"]
