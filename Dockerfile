# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install all Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    psutil \
    numpy \
    sqlalchemy \
    prometheus-client \
    slowapi \
    python-jose[cryptography] \
    passlib[bcrypt]==1.7.4 \
    bcrypt==4.0.1 \
    python-multipart \
    requests

# Copy the entire api folder into the container
COPY autoops/api/ .

# Copy logger from core folder
COPY autoops/core/logger.py .

# Copy auth.py specifically (in case it's separate)
COPY autoops/api/auth.py .

# Create logs directory inside container
RUN mkdir -p logs

# Expose port 8000
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]