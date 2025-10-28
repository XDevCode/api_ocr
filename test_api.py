#!/usr/bin/env python3
"""
Script de prueba para la API de OCR
"""

import requests
import base64
import json

def test_health():
    """Probar endpoint de salud"""
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error en health check: {e}")
        return False

def test_ocr_with_image():
    """Probar OCR con una imagen de prueba"""
    try:
        # Crear una imagen de prueba simple (texto blanco sobre fondo negro)
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Crear imagen de prueba
        img = Image.new('RGB', (400, 100), color='black')
        draw = ImageDraw.Draw(img)
        
        # Intentar usar una fuente del sistema, si no está disponible usar la por defecto
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 30), "HOLA MUNDO", fill='white', font=font)
        
        # Convertir a base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        # Enviar a la API
        headers = {
            'X-API-Key': 'tu_clave_segura_aqui',
            'Content-Type': 'application/json'
        }
        
        data = {
            'image_base64': f'data:image/png;base64,{img_base64}',
            'format': 'text'
        }
        
        response = requests.post('http://localhost:5000/ocr', headers=headers, json=data)
        print(f"OCR test: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error en OCR test: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Probando API de OCR...")
    
    # Probar health check
    if test_health():
        print("✅ Health check OK")
    else:
        print("❌ Health check FAILED")
        exit(1)
    
    # Probar OCR
    if test_ocr_with_image():
        print("✅ OCR test OK")
    else:
        print("❌ OCR test FAILED")
        exit(1)
    
    print("🎉 Todos los tests pasaron!")
