# handlers/backup.py
import json
import logging
import os
import requests

logger = logging.getLogger(__name__)

# Variables de entorno (se definen en Railway)
BACKUP_GIST_ID = os.environ.get("BACKUP_GIST_ID", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
BACKUP_GIST_FILENAME = "db_backup.json"

def guardar_backup_en_gist(datos_db):
    """
    Guarda la base de datos completa en un GitHub Gist.
    Retorna True si fue exitoso, False en caso contrario.
    """
    if not BACKUP_GIST_ID or not GITHUB_TOKEN:
        logger.error("BACKUP_GIST_ID o GITHUB_TOKEN no configurados")
        return False
    
    url = f"https://api.github.com/gists/{BACKUP_GIST_ID}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    contenido = json.dumps(datos_db, indent=2, ensure_ascii=False)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            gist_data = response.json()
            files = gist_data.get("files", {})
        else:
            files = {}
    except:
        files = {}
    
    files[BACKUP_GIST_FILENAME] = {"content": contenido}
    payload = {"files": files}
    
    try:
        response = requests.patch(url, headers=headers, json=payload, timeout=15)
        if response.status_code in [200, 201]:
            logger.info("Backup guardado exitosamente en GitHub Gist")
            return True
        else:
            logger.error(f"Error guardando backup: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Excepción guardando backup: {e}")
        return False

def cargar_backup_desde_gist():
    """
    Carga la base de datos desde un GitHub Gist.
    Retorna los datos o None si no existe o hay error.
    """
    if not BACKUP_GIST_ID or not GITHUB_TOKEN:
        logger.warning("BACKUP_GIST_ID o GITHUB_TOKEN no configurados")
        return None
    
    url = f"https://api.github.com/gists/{BACKUP_GIST_ID}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            gist_data = response.json()
            files = gist_data.get("files", {})
            
            if BACKUP_GIST_FILENAME in files:
                contenido_raw = files[BACKUP_GIST_FILENAME].get("content", "{}")
                datos = json.loads(contenido_raw)
                logger.info("Backup cargado exitosamente desde GitHub Gist")
                return datos
            else:
                logger.info("No se encontró archivo de backup en el Gist")
                return None
        else:
            logger.info(f"No se pudo cargar backup: HTTP {