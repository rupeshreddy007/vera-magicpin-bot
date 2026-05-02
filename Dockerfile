FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot_server.py .
COPY vera_composer.py .
COPY dataset/ ./dataset/

# Generate expanded dataset at build time (optional)
RUN python dataset/generate_dataset.py --seed-dir dataset --out ./expanded || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/v1/healthz')" || exit 1

# Run bot with uvicorn
CMD ["python", "-m", "uvicorn", "bot_server:app", "--host", "0.0.0.0", "--port", "8000"]
