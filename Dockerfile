FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure the static folder exists
RUN mkdir -p static

# Expose port (Render uses 10000 by default)
EXPOSE 10000

# Start the application
CMD ["python", "app.py"]