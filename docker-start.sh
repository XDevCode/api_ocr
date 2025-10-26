#!/bin/bash

# Script para iniciar la API de OCR con Docker
# Este script construye y ejecuta el contenedor Docker

set -e

echo "Iniciando API de OCR con Docker..."

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Docker no está instalado. Por favor instálelo primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose no está instalado. Por favor instálelo primero."
    exit 1
fi

# Crear directorio de logs
mkdir -p logs

# Verificar si existe el archivo de configuración
if [ ! -f ".env" ]; then
    echo "Archivo .env no encontrado. Creando uno por defecto..."
    cat > .env << EOF
# Configuración del servidor
HOST=0.0.0.0
PORT=5000
DEBUG=False

# Configuración de la cola de procesamiento
MAX_QUEUE_SIZE=10
MAX_WORKERS=2
TIMEOUT_SECONDS=30

# Configuración de OCR
OCR_LANGUAGES=es,en
USE_GPU=False

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/ocr_service.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# Configuración de seguridad
API_KEY=your_secure_api_key_here
ENABLE_API_KEY=True

# Configuración de memoria
MAX_IMAGE_SIZE_MB=10
CLEANUP_INTERVAL=300
EOF
    echo "Archivo .env creado. Por favor, configure su API_KEY antes de continuar."
    echo "Edite el archivo .env y cambie 'your_secure_api_key_here' por una clave segura."
    read -p "¿Desea continuar con la configuración por defecto? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Operación cancelada."
        exit 1
    fi
fi

# Construir la imagen Docker
echo "Construyendo imagen Docker..."
docker-compose build
if [ $? -ne 0 ]; then
    echo "Error al construir la imagen Docker."
    exit 1
fi

# Iniciar el servicio
echo "Iniciando servicio..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "Error al iniciar el servicio."
    exit 1
fi

# Esperar a que el servicio esté listo
echo "Esperando a que el servicio esté listo..."
sleep 10

# Verificar el estado del servicio
echo "Verificando estado del servicio..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "Servicio iniciado correctamente!"
    echo "API disponible en: http://localhost:5000"
    echo "Health check: http://localhost:5000/health"
    echo "Estadísticas: http://localhost:5000/stats"
    echo ""
    echo "Para ver los logs: docker-compose logs -f"
    echo "Para detener: docker-compose down"
else
    echo "Error al iniciar el servicio. Verificando logs..."
    docker-compose logs
    exit 1
fi