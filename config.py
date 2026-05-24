# config.py
# ============================================================
# CONFIGURACIÓN DEL BOT - VERSIÓN CON GITHUB RELEASES
# ============================================================

import os
import json
import requests

# ============================================================
# CONFIGURACIÓN BÁSICA
# ============================================================

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8907545202:AAFH1we_J12zJhjDx1tCCZHddkLKT8x8naw")
MI_USER_ID = 6985343427
WALLET_DIRECCION = "TJmQHdTKygppAdoHJX4QWghSCqoKSqdYtN"

# ============================================================
# CONFIGURACIÓN DE GITHUB RELEASES
# ============================================================

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "luisenriquepupo16-rgb/Shopy_Bot"
RELEASE_TAG = "untagged-3866522ca4f8ac87ace6"  # <-- CORREGIDO con el tag real de tu release

# URLs de GitHub API
GITHUB_API_RELEASES = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{RELEASE_TAG}"
GITHUB_RAW_CONTENT = f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}"

# ============================================================
# MENSAJE DE PAGO
# ============================================================

MENSAJE_PAGO = """
💰 Payment Instructions:

1. Open your USDT wallet (TronLink, Trust Wallet, Binance, etc.)
2. Send exact amount to this address:
   `{direccion}`
3. Use *TRC-20* network (important, do not use other networks)
4. After sending, use /status {pago_id} to verify

⚠️ Script will be sent after manual confirmation.
"""

# ============================================================
# FUNCIONES PARA CARGAR SCRIPTS DESDE GITHUB RELEASES
# ============================================================

def cargar_scripts_desde_github():
    """
    Carga los scripts y metadatos desde GitHub Releases
    """
    PRECIOS = {}
    NOMBRES_SCRIPTS = {}
    DESCRIPCIONES_SCRIPTS = {}
    
    # Headers para autenticación en GitHub API
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    try:
        # Obtener información de la release desde GitHub API
        response = requests.get(GITHUB_API_RELEASES, headers=headers, timeout=10)
        
        if response.status_code == 200:
            release_data = response.json()
            assets = release_data.get("assets", [])
            
            # Buscar archivo de metadatos en los assets
            metadata_asset = None
            for asset in assets:
                if asset.get("name") == "metadata.json":
                    metadata_asset = asset
                    break
            
            if metadata_asset:
                # Descargar metadata.json
                metadata_url = metadata_asset.get("browser_download_url")
                meta_response = requests.get(metadata_url, timeout=10)
                
                if meta_response.status_code == 200:
                    data = meta_response.json()
                    for script_id, info in data.items():
                        PRECIOS[script_id] = info.get("precio", 15)
                        NOMBRES_SCRIPTS[script_id] = info.get("nombre", f"Script {script_id}")
                        DESCRIPCIONES_SCRIPTS[script_id] = info.get("descripcion", "No description")
                    
                    print(f"✅ Cargados {len(PRECIOS)} scripts desde GitHub Releases")
                else:
                    print(f"❌ Error descargando metadata: HTTP {meta_response.status_code}")
                    usar_fallback(PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS)
            else:
                print("⚠️ No se encontró metadata.json en la release")
                usar_fallback(PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS)
        else:
            print(f"❌ Error accediendo a GitHub API: HTTP {response.status_code}")
            usar_fallback(PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS)
            
    except Exception as e:
        print(f"❌ Error cargando scripts desde GitHub: {e}")
        usar_fallback(PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS)
    
    return PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS

def usar_fallback(PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS):
    """Fallback en caso de no poder acceder a GitHub"""
    PRECIOS["1"] = 15
    NOMBRES_SCRIPTS["1"] = "CSV Cleaner Professional"
    DESCRIPCIONES_SCRIPTS["1"] = "Cleans CSV files professionally: auto-detects format, repairs broken rows, removes duplicates, preview, and logs."

def descargar_script_desde_github(script_id):
    """
    Descarga un script desde GitHub Releases
    Retorna el contenido del archivo o None si falla
    """
    script_filename = f"script_{script_id}.zip"
    download_url = f"{GITHUB_RAW_CONTENT}/{script_filename}"
    
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    try:
        response = requests.get(download_url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            print(f"❌ Error descargando script {script_id}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error descargando script {script_id}: {e}")
        return None

# Cargar scripts automáticamente al iniciar
PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS = cargar_scripts_desde_github()