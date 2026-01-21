FROM python:3.11-slim

# Install system dependencies (OCR + OpenCV)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install python libraries
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy whole project files
COPY . .

# Expose port Render uses
EXPOSE 7860

# Start Flask app
CMD ["python", "AI_Cyber_Security_Platform/app.py"]
