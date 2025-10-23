FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app
ENV PORT=8501  # default for local runs

EXPOSE 8501
EXPOSE 8000

CMD ["supervisord", "-c", "/app/supervisord.conf"]
