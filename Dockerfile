FROM python:3.14-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
COPY data/ ./data

RUN mkdir -p data/output

ENV PYTHONUNBUFFERED=1

CMD ["python", "src/agent.py"]