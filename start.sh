#!/bin/bash

# Script de inicio para la API de OCR
# Este script configura el entorno y ejecuta la aplicación

set -e

echo "Iniciando API de OCR..."

# Crear directorio de logs si no existe
mkdir -p logs

# Verificar si existe el archivo de configuración
if [ ! -f ".env" ]; then
    echo "Archivo .env no encontrado. Creando uno por defecto..."
    cp env.example .env 2>/dev/null || {
        echo "No se pudo crear .env. Verifique la configuración."
        exit 1
    }
fi

# Cargar variables de entorno
export $(cat .env | grep -v '^#' | xargs)

# Verificar si se está ejecutando en Docker
if [ -f /.dockerenv ]; then
    echo "Ejecutando en contenedor Docker..."
    python app.py
else
    echo "Ejecutando en sistema local..."
    
    # Verificar si Python está instalado
    if ! command -v python3 &> /dev/null; then
        echo "Python3 no está instalado. Por favor instálelo primero."
        exit 1
    fi
    
    # Verificar si pip está instalado
    if ! command -v pip3 &> /dev/null; then
        echo "pip3 no está instalado. Por favor instálelo primero."
        exit 1
    fi
    
    # Instalar dependencias si no están instaladas
    if [ ! -d "venv" ]; then
        echo "Creando entorno virtual..."
        python3 -m venv venv
    fi
    
    echo "Activando entorno virtual..."
    source venv/bin/activate
    
    echo "Instalando dependencias..."
    pip install -r requirements.txt
    
    echo "Iniciando aplicación..."
    python app.py
fi
