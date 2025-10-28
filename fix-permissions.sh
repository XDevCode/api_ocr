#!/bin/bash

# Script para arreglar permisos en Raspberry Pi
echo "🔧 Arreglando permisos..."

# Crear directorio de logs si no existe
mkdir -p logs

# Dar permisos correctos al directorio de logs
chmod 777 logs

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cat > .env << EOF
API_KEY=tu_clave_segura_aqui
HOST=0.0.0.0
PORT=5000
DEBUG=False
MAX_QUEUE_SIZE=5
MAX_WORKERS=1
TIMEOUT_SECONDS=120
OCR_LANGUAGES=es,en
USE_GPU=False
LOG_LEVEL=INFO
LOG_FILE=/app/logs/ocr_service.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
MAX_IMAGE_SIZE_MB=5
ENABLE_API_KEY=True
CLEANUP_INTERVAL=300
EOF
fi

echo "✅ Permisos arreglados"
echo "📝 Edita el archivo .env para cambiar la API_KEY:"
echo "   nano .env"
