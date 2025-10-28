#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API de OCR con Flask - Servicio de procesamiento de imágenes
Soporta imágenes en binario y base64 con manejo de colas y procesamiento concurrente
"""

import os
import base64
import io
import gc
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from typing import Dict, Any, Optional, Union
import json

import easyocr
import numpy as np
import torch
from flask import Flask, request, jsonify, abort
from PIL import Image
from dotenv import load_dotenv
import structlog

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Configuración de la aplicación
class Config:
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Configuración de cola
    MAX_QUEUE_SIZE = int(os.getenv('MAX_QUEUE_SIZE', 10))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 2))
    TIMEOUT_SECONDS = int(os.getenv('TIMEOUT_SECONDS', 30))
    
    # Configuración de OCR
    OCR_LANGUAGES = os.getenv('OCR_LANGUAGES', 'es,en').split(',')
    USE_GPU = os.getenv('USE_GPU', 'False').lower() == 'true'
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'ocr_service.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # Configuración de seguridad
    API_KEY = os.getenv('API_KEY', 'your_secure_api_key_here')
    ENABLE_API_KEY = os.getenv('ENABLE_API_KEY', 'True').lower() == 'true'
    
    # Configuración de memoria
    MAX_IMAGE_SIZE_MB = int(os.getenv('MAX_IMAGE_SIZE_MB', 10))
    CLEANUP_INTERVAL = int(os.getenv('CLEANUP_INTERVAL', 300))

# Inicializar Flask
app = Flask(__name__)
app.config.from_object(Config)

# Configurar logging
def setup_logging():
    """Configura el sistema de logging solo en consola"""
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    # Solo usar consola para evitar problemas de permisos
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)

# Inicializar logging
setup_logging()

# Variables globales para el procesamiento
reader = None
processing_queue = Queue(maxsize=Config.MAX_QUEUE_SIZE)
executor = ThreadPoolExecutor(max_workers=Config.MAX_WORKERS)
processing_stats = {
    'total_processed': 0,
    'queue_size': 0,
    'active_workers': 0,
    'errors': 0
}

def load_ocr_model():
    """Carga el modelo de EasyOCR una sola vez al iniciar"""
    global reader
    try:
        logger.info("Cargando modelo de EasyOCR", languages=Config.OCR_LANGUAGES)
        reader = easyocr.Reader(Config.OCR_LANGUAGES, gpu=Config.USE_GPU)
        logger.info("Modelo de EasyOCR cargado exitosamente")
    except Exception as e:
        logger.error("Error fatal al cargar el modelo de EasyOCR", error=str(e))
        raise

def cleanup_memory():
    """Limpia la memoria GPU y CPU"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def validate_api_key():
    """Valida la API key si está habilitada"""
    if not Config.ENABLE_API_KEY:
        return True
    
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != Config.API_KEY:
        abort(401, description="API key inválida o faltante")
    return True

def validate_image_size(image_data: bytes) -> bool:
    """Valida que la imagen no exceda el tamaño máximo permitido"""
    size_mb = len(image_data) / (1024 * 1024)
    if size_mb > Config.MAX_IMAGE_SIZE_MB:
        logger.warning("Imagen demasiado grande", size_mb=size_mb, max_size=Config.MAX_IMAGE_SIZE_MB)
        return False
    return True

def process_image_ocr(image_data: bytes, output_format: str = 'text') -> Dict[str, Any]:
    """
    Procesa una imagen con OCR y devuelve el resultado en el formato especificado
    
    Args:
        image_data: Datos de la imagen en bytes
        output_format: Formato de salida ('text', 'json', 'detailed')
    
    Returns:
        Diccionario con el resultado del OCR
    """
    try:
        # Decodificar imagen usando PIL
        img = Image.open(io.BytesIO(image_data))
        
        # Convertir a RGB si es necesario
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convertir a numpy array para EasyOCR
        img_array = np.array(img)
        
        results = reader.readtext(img_array, detail=1, paragraph=False)
        
        del img, img_array
        cleanup_memory()
        
        if output_format == 'text':
            text_lines = [result[1] for result in results]
            return {
                'success': True,
                'text': '\n'.join(text_lines),
                'format': 'text',
                'lines_count': len(text_lines)
            }
        
        elif output_format == 'json':
            text_lines = [result[1] for result in results]
            return {
                'success': True,
                'text': '\n'.join(text_lines),
                'format': 'json',
                'lines_count': len(text_lines),
                'raw_results': results
            }
        
        elif output_format == 'detailed':
            detailed_results = []
            for i, (bbox, text, confidence) in enumerate(results):
                detailed_results.append({
                    'line_number': i + 1,
                    'text': text,
                    'confidence': float(confidence),
                    'bounding_box': {
                        'top_left': [int(bbox[0][0]), int(bbox[0][1])],
                        'top_right': [int(bbox[1][0]), int(bbox[1][1])],
                        'bottom_right': [int(bbox[2][0]), int(bbox[2][1])],
                        'bottom_left': [int(bbox[3][0]), int(bbox[3][1])]
                    }
                })
            
            return {
                'success': True,
                'format': 'detailed',
                'lines_count': len(detailed_results),
                'results': detailed_results
            }
        
        else:
            raise ValueError(f"Formato de salida no válido: {output_format}")
            
    except Exception as e:
        logger.error("Error durante el procesamiento de OCR", error=str(e))
        cleanup_memory()
        raise

def worker_thread():
    """Hilo trabajador que procesa las imágenes de la cola"""
    while True:
        try:
            task = processing_queue.get(timeout=1)
            if task is None:
                break
                
            processing_stats['active_workers'] += 1
            processing_stats['queue_size'] = processing_queue.qsize()
            
            try:
                result = process_image_ocr(task['image_data'], task['output_format'])
                task['future'].set_result(result)
                processing_stats['total_processed'] += 1
                
            except Exception as e:
                logger.error("Error en procesamiento", error=str(e))
                processing_stats['errors'] += 1
                task['future'].set_exception(e)
            
            finally:
                processing_stats['active_workers'] -= 1
                processing_stats['queue_size'] = processing_queue.qsize()
                processing_queue.task_done()
                
        except Empty:
            continue
        except Exception as e:
            logger.error("Error en hilo trabajador", error=str(e))

worker_threads = []
for i in range(Config.MAX_WORKERS):
    thread = threading.Thread(target=worker_thread, daemon=True)
    thread.start()
    worker_threads.append(thread)

load_ocr_model()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servicio"""
    return jsonify({
        'status': 'healthy',
        'service': 'OCR API',
        'version': '1.0.0',
        'stats': processing_stats
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Endpoint para obtener estadísticas del servicio"""
    validate_api_key()
    return jsonify({
        'stats': processing_stats,
        'config': {
            'max_queue_size': Config.MAX_QUEUE_SIZE,
            'max_workers': Config.MAX_WORKERS,
            'timeout_seconds': Config.TIMEOUT_SECONDS
        }
    })

@app.route('/ocr', methods=['POST'])
def perform_ocr():
    """
    Endpoint principal para procesamiento de OCR
    
    Parámetros:
    - image: Archivo de imagen (multipart/form-data)
    - image_base64: Imagen en base64 (application/json)
    - format: Formato de salida ('text', 'json', 'detailed')
    - output_format: Alias para format
    """
    validate_api_key()
    
    try:
        # Obtener formato de salida
        output_format = request.form.get('format') or request.form.get('output_format') or 'text'
        if output_format not in ['text', 'json', 'detailed']:
            return jsonify({
                'success': False,
                'error': 'Formato de salida inválido. Use: text, json, o detailed'
            }), 400
        
        image_data = None
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_data = file.read()
                logger.info("Imagen recibida como archivo", filename=file.filename)
        
        elif request.is_json and 'image_base64' in request.json:
            base64_data = request.json['image_base64']
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            image_data = base64.b64decode(base64_data)
            logger.info("Imagen recibida como base64")
        
        else:
            return jsonify({
                'success': False,
                'error': 'No se proporcionó imagen válida. Use "image" (archivo) o "image_base64" (JSON)'
            }), 400
        
        if not validate_image_size(image_data):
            return jsonify({
                'success': False,
                'error': f'Imagen demasiado grande. Máximo: {Config.MAX_IMAGE_SIZE_MB}MB'
            }), 400
        
        if processing_queue.full():
            logger.warning("Cola de procesamiento llena")
            return jsonify({
                'success': False,
                'error': 'Servicio saturado. Intente más tarde.'
            }), 503
        
        import concurrent.futures
        future = concurrent.futures.Future()
        
        task = {
            'image_data': image_data,
            'output_format': output_format,
            'future': future,
            'timestamp': time.time()
        }
        
        processing_queue.put(task)
        logger.info("Tarea agregada a la cola", queue_size=processing_queue.qsize())
        
        try:
            result = future.result(timeout=Config.TIMEOUT_SECONDS)
            return jsonify(result)
            
        except concurrent.futures.TimeoutError:
            logger.error("Timeout en procesamiento")
            return jsonify({
                'success': False,
                'error': 'Timeout en el procesamiento de la imagen'
            }), 408
            
    except Exception as e:
        logger.error("Error en endpoint OCR", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@app.route('/ocr/sync', methods=['POST'])
def perform_ocr_sync():
    """
    Endpoint síncrono para procesamiento de OCR (para pruebas)
    """
    validate_api_key()
    
    try:
        # Obtener formato de salida
        output_format = request.form.get('format') or request.form.get('output_format') or 'text'
        if output_format not in ['text', 'json', 'detailed']:
            return jsonify({
                'success': False,
                'error': 'Formato de salida inválido. Use: text, json, o detailed'
            }), 400
        
        image_data = None
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_data = file.read()
        elif request.is_json and 'image_base64' in request.json:
            base64_data = request.json['image_base64']
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            image_data = base64.b64decode(base64_data)
        else:
            return jsonify({
                'success': False,
                'error': 'No se proporcionó imagen válida'
            }), 400
        
        if not validate_image_size(image_data):
            return jsonify({
                'success': False,
                'error': f'Imagen demasiado grande. Máximo: {Config.MAX_IMAGE_SIZE_MB}MB'
            }), 400
        
        result = process_image_ocr(image_data, output_format)
        return jsonify(result)
        
    except Exception as e:
        logger.error("Error en endpoint OCR síncrono", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

if __name__ == '__main__':
    logger.info("Iniciando servidor OCR", host=Config.HOST, port=Config.PORT)
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        threaded=True
    )
