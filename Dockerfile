FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install supervisor
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8501

# Expose ports
EXPOSE 8501
EXPOSE 8000

# Start supervisor (runs API + Streamlit)
CMD ["supervisord", "-c", "/app/supervisord.conf"]
