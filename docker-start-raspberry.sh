#!/bin/bash

# Script de inicio optimizado para Raspberry Pi
echo "🚀 Iniciando API de OCR en Raspberry Pi..."

# Verificar que Docker esté funcionando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está funcionando. Iniciando Docker..."
    sudo systemctl start docker
    sleep 5
fi

# Crear directorio de logs si no existe
mkdir -p logs

# Verificar que el archivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado. Creando uno básico..."
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
    echo "📝 Archivo .env creado. Edita la API_KEY antes de continuar."
    echo "   nano .env"
    exit 1
fi

# Limpiar contenedores anteriores
echo "🧹 Limpiando contenedores anteriores..."
docker compose down 2>/dev/null || true

# Construir y ejecutar
echo "🔨 Construyendo imagen..."
docker compose build --no-cache

echo "🚀 Iniciando servicio..."
docker compose up -d

# Esperar a que el servicio esté listo
echo "⏳ Esperando a que el servicio esté listo..."
sleep 10

# Verificar que funciona
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ API de OCR iniciada correctamente!"
    echo "🌐 Servicio disponible en: http://localhost:5000"
    echo "📊 Health check: http://localhost:5000/health"
    echo "📝 Logs: docker compose logs -f"
else
    echo "❌ Error al iniciar el servicio. Verificando logs..."
    docker compose logs
fi
