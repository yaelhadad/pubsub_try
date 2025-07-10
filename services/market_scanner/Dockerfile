FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared components
COPY shared/ ./shared/

# Copy service files
COPY services/market_scanner/ ./services/market_scanner/

# Set Python path to include shared modules
ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 5000

# Change to service directory
WORKDIR /app/services/market_scanner

CMD ["python", "app.py"] 