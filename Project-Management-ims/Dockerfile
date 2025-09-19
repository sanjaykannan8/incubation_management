FROM python:3.12-slim

# Update system packages and remove package cache to reduce vulnerabilities
RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Copy and install requirements as root first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and change ownership to app user
COPY . .
RUN chown -R app:app /app

# Switch to non-root user
USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]