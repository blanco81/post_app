FROM python:3.10-slim
WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y build-essential libpq-dev && \
    pip install --no-cache-dir -r requirements.txt --timeout=100 --retries=5

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
