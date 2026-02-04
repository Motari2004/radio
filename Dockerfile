# Use Playwright Python base image
FROM mcr.microsoft.com/playwright/python:v1.38.0-jammy

WORKDIR /app

# Copy requirements and bot
COPY requirements.txt bot.py ./ 
COPY static ./static

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port for Render
EXPOSE 10000

# Start the bot
CMD ["python", "bot.py"]
