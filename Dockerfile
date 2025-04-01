FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["sh", "-c", "uvicorn keepalive_server:app --host 0.0.0.0 --port 8080 & python telegram_supplement_bot_v2.py"]