# API de OCR con Flask

API para procesamiento de imágenes con OCR (Reconocimiento Óptico de Caracteres) usando Flask y EasyOCR. Optimizada para Raspberry Pi y cualquier plataforma con Python.

## Características

- Procesamiento asíncrono con cola de tareas
- Soporte para imágenes binarias y base64
- Formatos de salida configurables (texto, JSON, detallado)
- Contenedorización con Docker para ARM (Raspberry Pi)
- API Key para seguridad
- Monitoreo con endpoints de salud

## Despliegue

### Opción 1: Docker en Raspberry Pi

#### Instalación de Docker
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Reiniciar sesión
logout
```

#### Configuración y ejecución
```bash
# Clonar repositorio
git clone <tu-repositorio>
cd orc_api

# Configurar variables de entorno
cp env.example .env
nano .env  # Editar API_KEY y otras configuraciones

# Ejecutar con Docker
chmod +x docker-start.sh
./docker-start.sh
```

### Opción 2: Portainer

1. **Instalar Portainer**
```bash
docker volume create portainer_data
docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```

2. **Crear stack en Portainer**
   - Ir a `Stacks` > `Add stack`
   - Nombre: `ocr-api`
   - Usar el contenido de `docker-compose.yml`
   - Configurar variables de entorno (especialmente `API_KEY`)

### Opción 3: Ejecución directa con Python

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
nano .env

# Ejecutar
python app.py
```

## Configuración

### Variables principales (.env)
```env
HOST=0.0.0.0
PORT=5000
API_KEY=tu_clave_segura
MAX_QUEUE_SIZE=10
MAX_WORKERS=2
TIMEOUT_SECONDS=30
OCR_LANGUAGES=es,en
MAX_IMAGE_SIZE_MB=10
```

## Uso de la API

### Endpoints

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/health` | GET | Estado del servicio | No |
| `/stats` | GET | Estadísticas | Sí |
| `/ocr` | POST | Procesamiento asíncrono | Sí |
| `/ocr/sync` | POST | Procesamiento síncrono | Sí |

### Autenticación
```bash
X-API-Key: tu_clave_segura
```

### Ejemplos con curl

#### 1. Health Check
```bash
curl http://localhost:5000/health
```

#### 2. Estadísticas
```bash
curl -H "X-API-Key: tu_clave_segura" http://localhost:5000/stats
```

#### 3. Procesar imagen como archivo
```bash
curl -X POST http://localhost:5000/ocr \
  -H "X-API-Key: tu_clave_segura" \
  -F "image=@imagen.jpg" \
  -F "format=text"
```

#### 4. Procesar imagen en base64
```bash
curl -X POST http://localhost:5000/ocr \
  -H "X-API-Key: tu_clave_segura" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "format": "detailed"
  }'
```

#### 5. Procesamiento síncrono (para pruebas)
```bash
curl -X POST http://localhost:5000/ocr/sync \
  -H "X-API-Key: tu_clave_segura" \
  -F "image=@imagen.jpg" \
  -F "format=json"
```

### Formatos de salida

#### Texto simple (`format=text`)
```json
{
  "success": true,
  "text": "Texto extraído de la imagen",
  "format": "text",
  "lines_count": 1
}
```

#### JSON detallado (`format=json`)
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

#### Información completa (`format=detailed`)
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

## Monitoreo

### Ver logs
```bash
# Docker
docker-compose logs -f

# Ejecución directa
tail -f logs/ocr_service.log
```

### Verificar estado
```bash
# Health check
curl http://localhost:5000/health

# Estadísticas
curl -H "X-API-Key: tu_clave_segura" http://localhost:5000/stats
```

## Solución de problemas

### Error: "Servicio saturado"
- Aumentar `MAX_QUEUE_SIZE` y `MAX_WORKERS` en `.env`

### Error: "Imagen demasiado grande"
- Aumentar `MAX_IMAGE_SIZE_MB` en `.env`

### Error: "Timeout en procesamiento"
- Aumentar `TIMEOUT_SECONDS` en `.env`

### Error: "API key inválida"
- Verificar que `API_KEY` esté configurada correctamente
- Incluir header `X-API-Key` en las peticiones

## Configuración recomendada

### Raspberry Pi
```env
MAX_WORKERS=1
MAX_QUEUE_SIZE=5
TIMEOUT_SECONDS=120
MAX_IMAGE_SIZE_MB=5
```

### Servidor potente
```env
MAX_WORKERS=4
MAX_QUEUE_SIZE=20
TIMEOUT_SECONDS=60
MAX_IMAGE_SIZE_MB=20
```

## Requisitos

- Python 3.9+
- Docker (opcional)
- 2GB RAM mínimo (recomendado 4GB)
- 1GB espacio en disco