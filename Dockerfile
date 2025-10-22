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
    supervisor \          # ✅ ensure supervisor is installed for CMD
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ============================
# 5️⃣ Install Python dependencies
# ============================
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ============================
# 6️⃣ Expose ports
# ============================
EXPOSE 8000     # FastAPI
EXPOSE 8501     # Streamlit

# ============================
# 7️⃣ Start both services
# ============================
CMD ["supervisord", "-c", "/app/supervisord.conf"]
