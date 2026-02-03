# Use an official Playwright Python image with browsers preinstalled
FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

# Set working directory
WORKDIR /app

# Copy code
COPY bot.py requirements.txt ./

# Install Python deps (Playwright already available in image, but this ensures versions)
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the HTTP port for screenshot endpoint
EXPOSE 10000

# Start the bot
CMD ["python", "bot.py"]
