FROM python:3.9-slim

# Instalar dependencias básicas
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Crear directorio de logs con permisos correctos
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Crear usuario no-root ANTES de copiar archivos
RUN useradd -m -u 1000 appuser

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Dar permisos correctos al usuario
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 5000

# Comando de inicio
CMD ["python", "app.py"]