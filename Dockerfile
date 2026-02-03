FROM mcr.microsoft.com/playwright/python:v1.38.0-jammy

WORKDIR /app
COPY requirements.txt bot.py ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 10000

CMD ["python", "bot.py"]
