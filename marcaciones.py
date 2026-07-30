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
import pytz  # ⬅️ NUEVA DEPENDENCIA

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
MARGEN_MINUTOS = 2

# ⬇️ NUEVO: Configurar zona horaria de Chile
ZONA_HORARIA = pytz.timezone('America/Santiago')

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def obtener_hora_chile():
    """Obtiene la hora actual en zona horaria de Chile"""
    utc_now = datetime.now(pytz.UTC)
    chile_time = utc_now.astimezone(ZONA_HORARIA)
    return chile_time

def enviar_marcacion(tipo_marcacion):
    """Envía la marcación a la API"""
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
    """Determina si debe enviar marcación en este momento (hora Chile)"""
    # ⬇️ USAR HORA DE CHILE
    ahora = obtener_hora_chile()
    dia = ahora.weekday()
    hora = ahora.hour
    minuto = ahora.minute
    segundo = ahora.second
    
    logger.info(f"📅 Fecha actual (Chile): {ahora.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info(f"   Día: {dia} (0=Lunes, 4=Viernes)")
    logger.info(f"   Hora: {hora:02d}:{minuto:02d}:{segundo:02d}")
    
    # Verificar si es fin de semana
    if dia >= 5:
        logger.info("   ⏰ Es fin de semana - No hay marcaciones")
        return None
    
    # Verificar entrada (9:00)
    if hora == 9 and minuto <= MARGEN_MINUTOS:
        logger.info("   ⏰ Hora de marcación: ENTRADA (9:00 AM)")
        return 4
    
    # Verificar salida Lunes-Jueves (18:30)
    if dia <= 3 and hora == 18 and minuto >= (30 - MARGEN_MINUTOS) and minuto <= (30 + MARGEN_MINUTOS):
        logger.info(f"   ⏰ Hora de marcación: SALIDA LUNES-JUEVES (18:30 PM)")
        return 0
    
    # Verificar salida Viernes (18:00)
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
    
    logger.info(f"📋 Configuración:")
    logger.info(f"   RUT: {RUT}")
    logger.info(f"   Password: {'*' * len(PASSWORD)}")
    logger.info(f"   Margen: ±{MARGEN_MINUTOS} minutos")
    logger.info(f"   Zona Horaria: {ZONA_HORARIA}")
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
