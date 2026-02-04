FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Force install the specific browsers for this playwright version
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .
RUN mkdir -p static

EXPOSE 10000

CMD ["python", "app.py"]