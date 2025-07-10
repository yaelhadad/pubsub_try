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
COPY services/news_analyzer/ ./services/news_analyzer/

# Set Python path to include shared modules
ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 5001

# Change to service directory
WORKDIR /app/services/news_analyzer

CMD ["python", "app.py"] 