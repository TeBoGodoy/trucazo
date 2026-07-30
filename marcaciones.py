"""
Script de marcaciones automáticas para GitHub Actions
Ejecuta marcaciones según horario: Lunes-Viernes 9:00, Lunes-Jueves 18:30, Viernes 18:00
Siempre usa markType: 4 (como en el ejemplo original)
"""

import requests
import json
from datetime import datetime
import os
import sys
import logging
import pytz

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

# ⬇️ CONFIGURACIÓN DESDE VARIABLES DE ENTORNO
URL_API = os.environ.get('URL_API')
RUT = os.environ.get('RUT')
PASSWORD = os.environ.get('PASSWORD')

# ⬇️ VALIDAR QUE TODAS LAS VARIABLES EXISTEN
variables_requeridas = {
    'URL_API': URL_API,
    'RUT': RUT,
    'PASSWORD': PASSWORD
}

errores = False
for var_name, var_value in variables_requeridas.items():
    if not var_value:
        logger.error(f"❌ ERROR: Variable de entorno {var_name} no configurada")
        logger.error(f"   Configúrala en GitHub: Settings → Secrets → {var_name}")
        errores = True

if errores:
    sys.exit(1)

# ⬇️ CONSTANTE: SIEMPRE USA 4
MARK_TYPE = 4

MARGEN_MINUTOS = 2
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

def enviar_marcacion():
    """Envía la marcación a la API SIEMPRE con markType: 4"""
    data = {
        "body": {
            "rut": RUT,
            "password": PASSWORD,
            "markType": MARK_TYPE  # Siempre 4
        }
    }
    
    try:
        logger.info(f"📤 Enviando marcación con markType: {MARK_TYPE}")
        logger.info(f"   RUT: {RUT}")
        logger.info(f"   URL: {URL_API}")
        logger.info(f"   Payload: {json.dumps(data, indent=2)}")
        
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
        return False
    
    # Verificar entrada (9:00)
    if hora == 9 and minuto <= MARGEN_MINUTOS:
        logger.info("   ⏰ Hora de marcación: ENTRADA (9:00 AM)")
        return True
    
    # Verificar salida Lunes-Jueves (18:30)
    if dia <= 3 and hora == 18 and minuto >= (30 - MARGEN_MINUTOS) and minuto <= (30 + MARGEN_MINUTOS):
        logger.info(f"   ⏰ Hora de marcación: SALIDA LUNES-JUEVES (18:30 PM)")
        return True
    
    # Verificar salida Viernes (18:00)
    if dia == 4 and hora == 18 and minuto <= MARGEN_MINUTOS:
        logger.info("   ⏰ Hora de marcación: SALIDA VIERNES (18:00 PM)")
        return True
    
    logger.info("   ⏰ No es hora de marcación")
    return False

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("🚀 INICIANDO PROCESO DE MARCACIONES")
    logger.info("=" * 60)
    
    logger.info(f"📋 Configuración:")
    logger.info(f"   URL API: {URL_API}")
    logger.info(f"   RUT: {RUT[:4]}******-{RUT[-1]}")  # Muestra solo parte del RUT
    logger.info(f"   Password: {'*' * len(PASSWORD)}")
    logger.info(f"   MarkType: {MARK_TYPE} (SIEMPRE 4)")
    logger.info(f"   Margen: ±{MARGEN_MINUTOS} minutos")
    logger.info(f"   Zona Horaria: {ZONA_HORARIA}")
    
    debe_enviar = debe_enviar_marcacion()
    
    if debe_enviar:
        logger.info("-" * 40)
        exito = enviar_marcacion()
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
