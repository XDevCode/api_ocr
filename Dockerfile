# Dockerfile para API de OCR - Raspberry Pi ARM
FROM python:3.9-slim

# Metadatos
LABEL maintainer="OCR API Service"
LABEL description="API de procesamiento de imágenes con OCR usando Flask y EasyOCR"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema para ARM
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app.py .
COPY env.example .

# Crear directorio para logs
RUN mkdir -p /app/logs

# Crear usuario no-root para seguridad
RUN groupadd -r ocruser && useradd -r -g ocruser ocruser
RUN chown -R ocruser:ocruser /app
USER ocruser

# Exponer puerto
EXPOSE 5000

# Variables de entorno por defecto
ENV HOST=0.0.0.0
ENV PORT=5000
ENV DEBUG=False
ENV MAX_QUEUE_SIZE=10
ENV MAX_WORKERS=2
ENV TIMEOUT_SECONDS=30
ENV OCR_LANGUAGES=es,en
ENV USE_GPU=False
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/app/logs/ocr_service.log
ENV MAX_IMAGE_SIZE_MB=10
ENV ENABLE_API_KEY=True
ENV API_KEY=your_secure_api_key_here

# Comando de inicio
CMD ["python", "app.py"]