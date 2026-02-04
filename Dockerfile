FROM mcr.microsoft.com/playwright/python:v1.38.0-jammy

WORKDIR /app

# Copy app files
COPY requirements.txt server.py static/ ./

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Ensure Playwright browsers are available
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Bind to Render's PORT
EXPOSE 10000

CMD ["python", "bot.py"]
