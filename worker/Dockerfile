FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir aio_pika httpx

CMD ["python", "executor.py"]
