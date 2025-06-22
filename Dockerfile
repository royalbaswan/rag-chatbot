# Use official Python base
FROM python:3.10-slim

# Setting Python env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git wget curl \
    && rm -rf /var/lib/apt/lists/*

# Creating working directory
WORKDIR /app

# Copying code and requirements
COPY . /app

# Installing Python dependencies
RUN pip install --upgrade pip

# Installing other project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Exposing port
EXPOSE 8000

# Entry point
CMD ["uvicorn", "app.main:app", "--log-config", "log_config.yaml", "--port", "8000"]
