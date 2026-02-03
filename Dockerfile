# Use Playwright official Python image (has all deps + browsers)
FROM mcr.microsoft.com/playwright/python:1.38.0-focal

# Set working directory
WORKDIR /app

# Copy your files
COPY requirements.txt bot.py ./

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port for screenshot endpoint
EXPOSE 10000

# Start the bot
CMD ["python", "bot.py"]
