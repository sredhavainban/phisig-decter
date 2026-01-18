FROM python:3.10-slim

# Prevent Python from writing pyc files and enable output buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies including Tesseract OCR and libraries needed by OpenCV
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       tesseract-ocr \
       libgl1 \
       libglib2.0-0 \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy application
COPY . /app

# Expose HF Spaces port
EXPOSE 7860

# Use gunicorn to serve the Flask app in production
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "AI_Cyber_Security_Platform.app:app", "--workers", "1", "--threads", "4"]
