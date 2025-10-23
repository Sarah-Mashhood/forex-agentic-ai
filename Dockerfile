# ============================
# 1️⃣ Base image
# ============================
FROM python:3.11-slim

# ============================
# 2️⃣ Set working directory
# ============================
WORKDIR /app

# ============================
# 3️⃣ Copy project files
# ============================
COPY . /app

# ============================
# 4️⃣ Install system dependencies
# ============================
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# ============================
# 5️⃣ Install Python dependencies
# ============================
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================
# 6️⃣ Expose ports
# ============================

# FastAPI (serves both API + dashboard)
EXPOSE 8080

# ============================
# 7️⃣ Default command
# ============================
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
