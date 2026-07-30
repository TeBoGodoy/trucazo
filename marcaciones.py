"""
Script de marcaciones automáticas para GitHub Actions
Ejecuta marcaciones según horario: Lunes-Viernes 9:00, Lunes-Jueves 18:30, Viernes 18:00
"""

import requests
import json
from datetime import datetime, date
import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('marcaciones.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuración
URL_API = "https://demo.izytimecontrol.com/api/employee/SendMarkWebV2"
RUT = os.environ.get('RUT', "17.978.432-7")
PASSWORD = os.environ.get('PASSWORD', "1111")
MARGEN_MINUTOS = 2  # Margen de 2 minutos para ejecución

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def enviar_marcacion(tipo_marcacion):
    """
    Envía la marcación a la API
    
    Args:
        tipo_marcacion (int): 4=Entrada, 0=Salida
    
    Returns:
        bool: True si fue exitoso, False si falló
    """
    data = {
        "body": {
            "rut": RUT,
            "password": PASSWORD,
            "markType": tipo_marcacion
        }
    }
    
    try:
        logger.info(f"📤 Enviando marcación tipo {tipo_marcacion}")
        logger.info(f"   RUT: {RUT}")
        logger.info(f"   URL: {URL_API}")
        
        response = requests.post(URL_API, json=data, headers=HEADERS, timeout=10)
        
        logger.info(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            respuesta_json = response.json()
            logger.info(f"   ✅ Éxito: {json.dumps(respuesta_json, indent=2)}")
            return True
        else:
            logger.error(f"   ❌ Error HTTP: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("   ❌ Timeout: La API no respondió en 10 segundos")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("   ❌ Error de conexión: No se pudo conectar a la API")
        return False
    except Exception as e:
        logger.error(f"   ❌ Error inesperado: {str(e)}")
        return False

def debe_enviar_marcacion():
    """
    Determina si debe enviar marcación en este momento
    
    Returns:
        int or None: Tipo de marcación o None si no debe enviar
    """
    ahora = datetime.now()
    dia = ahora.weekday()  # 0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, 4=Viernes
    hora = ahora.hour
    minuto = ahora.minute  # ✅ CORREGIDO: minute en lugar de minuto
    segundo = ahora.second
    
    logger.info(f"📅 Fecha actual: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"   Día: {dia} (0=Lunes, 4=Viernes)")
    logger.info(f"   Hora: {hora:02d}:{minuto:02d}:{segundo:02d}")
    
    # Verificar si es fin de semana (5=Sábado, 6=Domingo)
    if dia >= 5:
        logger.info("   ⏰ Es fin de semana - No hay marcaciones")
        return None
    
    # VERIFICAR MARCACIÓN DE ENTRADA (9:00)
    # Margen de 2 minutos (8:58 a 9:02)
    if hora == 9 and minuto <= MARGEN_MINUTOS:
        logger.info("   ⏰ Hora de marcación: ENTRADA (9:00 AM)")
        return 4
    
    # VERIFICAR MARCACIÓN DE SALIDA LUNES-JUEVES (18:30)
    # Margen de 2 minutos (18:28 a 18:32)
    if dia <= 3 and hora == 18 and minuto >= (30 - MARGEN_MINUTOS) and minuto <= (30 + MARGEN_MINUTOS):
        logger.info(f"   ⏰ Hora de marcación: SALIDA LUNES-JUEVES (18:30 PM) - Día {dia}")
        return 0
    
    # VERIFICAR MARCACIÓN DE SALIDA VIERNES (18:00)
    # Margen de 2 minutos (17:58 a 18:02)
    if dia == 4 and hora == 18 and minuto <= MARGEN_MINUTOS:
        logger.info("   ⏰ Hora de marcación: SALIDA VIERNES (18:00 PM)")
        return 0
    
    logger.info("   ⏰ No es hora de marcación")
    return None

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("🚀 INICIANDO PROCESO DE MARCACIONES")
    logger.info("=" * 60)
    
    # Mostrar configuración (ocultando contraseña por seguridad)
    logger.info(f"📋 Configuración:")
    logger.info(f"   RUT: {RUT}")
    logger.info(f"   Password: {'*' * len(PASSWORD)}")
    logger.info(f"   Margen: ±{MARGEN_MINUTOS} minutos")
    logger.info(f"   URL: {URL_API}")
    
    tipo_marcacion = debe_enviar_marcacion()
    
    if tipo_marcacion is not None:
        logger.info("-" * 40)
        exito = enviar_marcacion(tipo_marcacion)
        logger.info("-" * 40)
        
        if exito:
            logger.info("✅ PROCESO COMPLETADO CON ÉXITO")
            sys.exit(0)
        else:
            logger.error("❌ PROCESO COMPLETADO CON ERRORES")
            sys.exit(1)
    else:
        logger.info("✅ PROCESO COMPLETADO - SIN MARCACIONES PENDIENTES")
        sys.exit(0)

if __name__ == "__main__":
    main()
