# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install UV and curl for healthcheck
RUN apt-get update && apt-get install -y curl && \
    pip install --no-cache-dir uv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# Create virtual environment and install dependencies via UV
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e .

# Expose port
EXPOSE 8000

# Run application from virtual environment
CMD [".venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
