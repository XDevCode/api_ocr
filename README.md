# API de OCR con Flask

Una API eficiente y escalable para procesamiento de imágenes con OCR (Reconocimiento Óptico de Caracteres) usando Flask y EasyOCR. Diseñada para funcionar en Raspberry Pi y cualquier plataforma con Python.

## ¿Qué es esta API?

Esta API permite extraer texto de imágenes de forma automática usando tecnología OCR (Reconocimiento Óptico de Caracteres). Es perfecta para:

- **Automatización de documentos**: Procesar facturas, recibos, formularios
- **Integración con n8n**: Automatizar workflows con reconocimiento de texto
- **Procesamiento masivo**: Manejar múltiples imágenes simultáneamente
- **Aplicaciones IoT**: Usar en Raspberry Pi para proyectos de automatización

## ¿Cómo funciona?

1. **Recibe una imagen** (como archivo o en formato base64)
2. **La procesa con EasyOCR** usando modelos de IA pre-entrenados
3. **Extrae el texto** con coordenadas y nivel de confianza
4. **Devuelve el resultado** en formato JSON configurable

### Flujo de procesamiento:
```
Imagen → Cola de tareas → Workers concurrentes → EasyOCR → Resultado JSON
```

## Características

- **Procesamiento asíncrono** con cola de tareas y workers concurrentes
- **Soporte múltiple de formatos**: imágenes binarias y base64
- **Formatos de salida configurables**: texto simple, JSON detallado, o información completa con coordenadas
- **Sistema de colas** para manejar alta carga sin saturación
- **Logging estructurado** con rotación de archivos
- **Configuración flexible** mediante variables de entorno
- **Contenedorización** con Docker para Raspberry Pi ARM
- **API Key** para seguridad
- **Monitoreo** con endpoints de salud y estadísticas

## Requisitos

- Python 3.9+
- Docker y Docker Compose (opcional)
- 2GB RAM mínimo (recomendado 4GB)
- 1GB espacio en disco

## Instalación

### Opción 1: Ejecución Local

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd orc_api
```

2. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

3. **Ejecutar con script de inicio**
```bash
chmod +x start.sh
./start.sh
```

### Opción 2: Docker (Recomendado para Raspberry Pi)

#### Instalación de Docker en Raspberry Pi

1. **Actualizar el sistema**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Instalar Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

3. **Instalar Docker Compose**
```bash
sudo apt install docker-compose-plugin -y
# O para versiones más antiguas:
# sudo apt install docker-compose -y
```

4. **Reiniciar la sesión**
```bash
logout
# Volver a iniciar sesión
```

#### Configuración y ejecución

1. **Configurar variables de entorno**
```bash
# Editar .env con tus configuraciones, especialmente API_KEY
nano .env
```

2. **Ejecutar con Docker**
```bash
chmod +x docker-start.sh
./docker-start.sh
```

#### Verificación de instalación Docker
```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar que funciona
docker run hello-world
```

## Configuración

### Variables de Entorno Principales

```env
# Servidor
HOST=0.0.0.0
PORT=5000
DEBUG=False

# Cola de procesamiento
MAX_QUEUE_SIZE=10          # Máximo de imágenes en cola
MAX_WORKERS=2              # Número de workers concurrentes
TIMEOUT_SECONDS=30         # Timeout por tarea

# OCR
OCR_LANGUAGES=es,en        # Idiomas soportados
USE_GPU=False              # Usar GPU (requiere CUDA)

# Seguridad
API_KEY=tu_clave_segura    # Clave de API
ENABLE_API_KEY=True        # Habilitar autenticación

# Memoria
MAX_IMAGE_SIZE_MB=10       # Tamaño máximo de imagen
```

## Uso de la API

### Endpoints Disponibles

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/health` | GET | Estado del servicio | No |
| `/stats` | GET | Estadísticas de procesamiento | Sí |
| `/ocr` | POST | Procesamiento asíncrono de imágenes | Sí |
| `/ocr/sync` | POST | Procesamiento síncrono (para pruebas) | Sí |

### Autenticación

Todos los endpoints excepto `/health` requieren la API key en el header:
```bash
X-API-Key: tu_clave_segura
```

### Procesamiento de Imágenes

#### 1. Imagen como archivo (multipart/form-data)

**Con curl:**
```bash
curl -X POST http://localhost:5000/ocr \
  -H "X-API-Key: tu_clave_segura" \
  -F "image=@imagen.jpg" \
  -F "format=text"
```

**Con PowerShell:**
```powershell
$headers = @{"X-API-Key"="tu_clave_segura"}
$form = @{
    image = Get-Item "imagen.jpg"
    format = "text"
}
Invoke-RestMethod -Uri "http://localhost:5000/ocr" -Method Post -Headers $headers -Form $form
```

#### 2. Imagen en base64 (JSON)

**Con curl:**
```bash
curl -X POST http://localhost:5000/ocr \
  -H "X-API-Key: tu_clave_segura" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "format": "detailed"
  }'
```

**Con PowerShell:**
```powershell
$headers = @{
    "X-API-Key" = "tu_clave_segura"
    "Content-Type" = "application/json"
}
$body = @{
    image_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
    format = "detailed"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/ocr" -Method Post -Headers $headers -Body $body
```

#### 3. Verificar estado del servicio

```bash
# Health check
curl http://localhost:5000/health

# Estadísticas
curl -H "X-API-Key: tu_clave_segura" http://localhost:5000/stats
```

### Formatos de Salida

#### 1. Texto Simple (`format=text`)
```json
{
  "success": true,
  "text": "Texto extraído de la imagen",
  "format": "text",
  "lines_count": 1
}
```

#### 2. JSON Detallado (`format=json`)
```json
{
  "success": true,
  "text": "Texto extraído",
  "format": "json",
  "lines_count": 1,
  "raw_results": [
    [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], "texto", 0.95]
  ]
}
```

#### 3. Información Completa (`format=detailed`)
```json
{
  "success": true,
  "format": "detailed",
  "lines_count": 1,
  "results": [
    {
      "line_number": 1,
      "text": "texto extraído",
      "confidence": 0.95,
      "bounding_box": {
        "top_left": [x1, y1],
        "top_right": [x2, y2],
        "bottom_right": [x3, y3],
        "bottom_left": [x4, y4]
      }
    }
  ]
}
```

## Integración con n8n

### Configuración del nodo HTTP Request en n8n

1. **Método**: POST
2. **URL**: `http://tu-servidor:5000/ocr`
3. **Headers**:
   ```
   X-API-Key: tu_clave_segura
   Content-Type: application/json
   ```
4. **Body** (JSON):
   ```json
   {
     "image_base64": "{{ $json.image_base64 }}",
     "format": "text"
   }
   ```

### Ejemplo de workflow en n8n

```json
{
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "name": "OCR Processing",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:5000/ocr",
        "headers": {
          "X-API-Key": "tu_clave_segura",
          "Content-Type": "application/json"
        },
        "body": {
          "image_base64": "{{ $json.image }}",
          "format": "detailed"
        }
      }
    }
  ]
}
```

## Monitoreo

### Health Check
```bash
curl http://localhost:5000/health
```

### Estadísticas
```bash
curl -H "X-API-Key: tu_clave_segura" http://localhost:5000/stats
```

## Docker

### Construir imagen
```bash
docker build -t ocr-api .
```

### Ejecutar contenedor
```bash
docker run -d \
  --name ocr-api \
  -p 5000:5000 \
  -e API_KEY=tu_clave_segura \
  -v $(pwd)/logs:/app/logs \
  ocr-api
```

### Docker Compose
```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## Logs y Monitoreo

### Ubicación de los Logs

- **Ejecución local**: `logs/ocr_service.log`
- **Docker**: `/app/logs/ocr_service.log`
- **Docker Compose**: `./logs/ocr_service.log`

### Configuración de Logs

```env
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
LOG_FILE=ocr_service.log    # Archivo de log
LOG_MAX_SIZE=10485760       # 10MB por archivo
LOG_BACKUP_COUNT=5          # 5 archivos de respaldo
```

### Ver Logs en Tiempo Real

**Ejecución local:**
```bash
tail -f logs/ocr_service.log
```

**Docker:**
```bash
# Ver logs del contenedor
docker logs -f ocr-api-service

# Ver logs con docker-compose
docker-compose logs -f
```

**Docker con filtros:**
```bash
# Solo errores
docker logs ocr-api-service 2>&1 | grep ERROR

# Últimas 100 líneas
docker logs --tail 100 ocr-api-service
```

### Estructura de los Logs

Los logs están en formato JSON estructurado:
```json
{
  "timestamp": "2025-10-26T19:46:20.123456Z",
  "level": "info",
  "logger": "app",
  "message": "Tarea agregada a la cola",
  "queue_size": 2
}
```

### Monitoreo de Rendimiento

**Ver estadísticas en tiempo real:**
```bash
# Cada 5 segundos
watch -n 5 'curl -s -H "X-API-Key: tu_clave_segura" http://localhost:5000/stats | jq'

# Con curl simple
curl -H "X-API-Key: tu_clave_segura" http://localhost:5000/stats
```

**Respuesta de estadísticas:**
```json
{
  "stats": {
    "total_processed": 150,
    "queue_size": 2,
    "active_workers": 1,
    "errors": 3
  },
  "config": {
    "max_queue_size": 10,
    "max_workers": 2,
    "timeout_seconds": 30
  }
}
```

## Seguridad

- API Key obligatoria para todos los endpoints (excepto `/health`)
- Validación de tamaño de imagen
- Límites de memoria y procesamiento
- Usuario no-root en Docker
- Timeouts configurable

## Solución de Problemas

### Error: "Servicio saturado"
- Aumentar `MAX_QUEUE_SIZE` y `MAX_WORKERS`
- Verificar recursos del sistema

### Error: "Imagen demasiado grande"
- Aumentar `MAX_IMAGE_SIZE_MB`
- Comprimir la imagen antes de enviar

### Error: "Timeout en procesamiento"
- Aumentar `TIMEOUT_SECONDS`
- Verificar complejidad de la imagen

### Error: "API key inválida"
- Verificar que `API_KEY` esté configurada correctamente
- Incluir header `X-API-Key` en las peticiones

## Rendimiento

### Configuración Recomendada

**Desarrollo:**
- MAX_WORKERS: 2
- MAX_QUEUE_SIZE: 5
- TIMEOUT_SECONDS: 30

**Producción:**
- MAX_WORKERS: 4-8 (según CPU)
- MAX_QUEUE_SIZE: 20-50
- TIMEOUT_SECONDS: 60

### Optimizaciones

1. **GPU**: Habilitar `USE_GPU=True` si tienes CUDA
2. **Memoria**: Ajustar `MAX_IMAGE_SIZE_MB` según necesidades
3. **Workers**: Aumentar `MAX_WORKERS` para mayor concurrencia
4. **Cola**: Aumentar `MAX_QUEUE_SIZE` para manejar picos de tráfico

## Despliegue en Producción

### Configuración para Producción

1. **Configurar variables de entorno de producción**
```bash
# Editar .env para producción
nano .env
```

```env
# Configuración de producción
HOST=0.0.0.0
PORT=5000
DEBUG=False
MAX_QUEUE_SIZE=50
MAX_WORKERS=4
TIMEOUT_SECONDS=60
API_KEY=clave_super_segura_de_produccion
ENABLE_API_KEY=True
LOG_LEVEL=INFO
```

2. **Usar Docker Compose para producción**
```bash
# Iniciar en segundo plano
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### Configuración de Servidor Web (Nginx)

**Instalar Nginx:**
```bash
sudo apt update
sudo apt install nginx -y
```

**Configurar Nginx:**
```bash
sudo nano /etc/nginx/sites-available/ocr-api
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

**Activar configuración:**
```bash
sudo ln -s /etc/nginx/sites-available/ocr-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Configuración de SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com

# Renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Configuración de Firewall

```bash
# Configurar UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Monitoreo y Mantenimiento

**Script de monitoreo:**
```bash
#!/bin/bash
# monitor.sh
while true; do
    if ! curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "API no responde, reiniciando..."
        docker-compose restart
    fi
    sleep 30
done
```

**Cron para limpieza de logs:**
```bash
# Agregar a crontab
0 2 * * * find /ruta/a/logs -name "*.log.*" -mtime +7 -delete
```

## Raspberry Pi

### Configuración Específica para Raspberry Pi

El Dockerfile está optimizado para arquitectura ARM (Raspberry Pi):

```bash
# Construir para ARM
docker buildx build --platform linux/arm64 -t ocr-api .

# O usar docker-compose
docker-compose up -d
```

### Recursos Recomendados para Raspberry Pi

- **Raspberry Pi 4**: 4GB RAM mínimo (recomendado 8GB)
- **Raspberry Pi 3**: 2GB RAM (puede ser lento)
- **Almacenamiento**: 16GB mínimo para el contenedor
- **MicroSD**: Clase 10 o superior

### Optimizaciones para Raspberry Pi

**Configuración .env optimizada:**
```env
# Configuración optimizada para Raspberry Pi
MAX_QUEUE_SIZE=5
MAX_WORKERS=1
TIMEOUT_SECONDS=120
MAX_IMAGE_SIZE_MB=5
USE_GPU=False
```

**Configuración de memoria:**
```bash
# Aumentar memoria para GPU (opcional)
sudo raspi-config
# Advanced Options > Memory Split > 128
```

### Inicio Automático en Raspberry Pi

**Crear servicio systemd:**
```bash
sudo nano /etc/systemd/system/ocr-api.service
```

```ini
[Unit]
Description=OCR API Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/pi/orc_api
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

**Activar servicio:**
```bash
sudo systemctl enable ocr-api.service
sudo systemctl start ocr-api.service
```

## Ejemplos Prácticos

### Ejemplo 1: Procesar una factura

```bash
# Subir imagen de factura
curl -X POST http://localhost:5000/ocr \
  -H "X-API-Key: tu_clave_segura" \
  -F "image=@factura.jpg" \
  -F "format=detailed"
```

**Respuesta:**
```json
{
  "success": true,
  "format": "detailed",
  "lines_count": 8,
  "results": [
    {
      "line_number": 1,
      "text": "FACTURA #12345",
      "confidence": 0.98,
      "bounding_box": {...}
    },
    {
      "line_number": 2,
      "text": "Fecha: 26/10/2025",
      "confidence": 0.95,
      "bounding_box": {...}
    }
  ]
}
```

### Ejemplo 2: Integración con n8n

**Nodo HTTP Request en n8n:**
- **URL**: `http://tu-servidor:5000/ocr`
- **Método**: POST
- **Headers**: `{"X-API-Key": "tu_clave_segura"}`
- **Body**:
```json
{
  "image_base64": "{{ $json.image_base64 }}",
  "format": "text"
}
```

### Ejemplo 3: Script de procesamiento masivo

```python
import requests
import base64
import os

def process_images_folder(folder_path, api_key):
    """Procesa todas las imágenes de una carpeta"""
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            with open(os.path.join(folder_path, filename), 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = requests.post(
                'http://localhost:5000/ocr',
                headers={'X-API-Key': api_key},
                json={
                    'image_base64': f'data:image/jpeg;base64,{image_base64}',
                    'format': 'text'
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"{filename}: {result['text']}")
            else:
                print(f"Error procesando {filename}: {response.text}")

# Usar
process_images_folder('./imagenes', 'tu_clave_segura')
```

## Troubleshooting

### Problemas Comunes

**1. Error: "Servicio saturado"**
```bash
# Solución: Aumentar capacidad
# Editar .env
MAX_QUEUE_SIZE=20
MAX_WORKERS=4
```

**2. Error: "Imagen demasiado grande"**
```bash
# Solución: Aumentar límite o comprimir imagen
MAX_IMAGE_SIZE_MB=20
```

**3. Error: "Timeout en procesamiento"**
```bash
# Solución: Aumentar timeout
TIMEOUT_SECONDS=120
```

**4. Docker no inicia en Raspberry Pi**
```bash
# Verificar arquitectura
uname -m
# Debe ser aarch64 para ARM64

# Reconstruir imagen
docker-compose build --no-cache
```

**5. API no responde**
```bash
# Verificar logs
docker-compose logs

# Verificar puerto
netstat -tlnp | grep 5000

# Reiniciar servicio
docker-compose restart
```

### Comandos de Diagnóstico

```bash
# Verificar estado del contenedor
docker-compose ps

# Ver uso de recursos
docker stats

# Ver logs en tiempo real
docker-compose logs -f --tail=100

# Verificar conectividad
curl -v http://localhost:5000/health

# Verificar configuración
docker-compose config
```

### Optimización de Rendimiento

**Para Raspberry Pi:**
```env
MAX_WORKERS=1
MAX_QUEUE_SIZE=3
TIMEOUT_SECONDS=180
MAX_IMAGE_SIZE_MB=3
```

**Para servidor potente:**
```env
MAX_WORKERS=8
MAX_QUEUE_SIZE=100
TIMEOUT_SECONDS=30
MAX_IMAGE_SIZE_MB=50
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de Troubleshooting
2. Verifica los logs del servicio
3. Comprueba la configuración en `.env`
4. Abre un issue en el repositorio

---

**¡Tu API de OCR está lista para usar!** 🚀