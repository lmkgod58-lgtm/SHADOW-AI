FROM python:3.11-slim

# Install build tools + terminal recon tools
RUN apt-get update && apt-get install -y     build-essential cmake git wget curl     lynx whois dnsutils     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Pre-download model (best effort — falls back to runtime)
RUN mkdir -p /app/models &&     wget -q --timeout=60 -O /app/models/model.gguf     https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q3_k_s.gguf ||     echo "Model pre-download failed — will retry at runtime"

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
