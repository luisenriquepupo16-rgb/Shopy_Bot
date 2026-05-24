# config.py
# ============================================================
# CONFIGURACIÓN DEL BOT - VERSIÓN ESTABLE
# ============================================================

import os
import json

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8907545202:AAFH1we_J12zJhjDx1tCCZHddkLKT8x8naw")
MI_USER_ID = 6985343427
WALLET_DIRECCION = "   TJmQHdTKygppAdoHJX4QWghSCqoKSqdYtN"  

MENSAJE_PAGO = """
💰 Payment Instructions:

1. Open your USDT wallet (TronLink, Trust Wallet, Binance, etc.)
2. Send exact amount to this address:
   `{direccion}`
3. Use *TRC-20* network (important, do not use other networks)
4. After sending, use /status {pago_id} to verify

⚠️ Script will be sent after manual confirmation.
"""

def cargar_scripts_desde_carpeta():
    metadata_path = "scripts/metadata.json"
    PRECIOS = {}
    NOMBRES_SCRIPTS = {}
    DESCRIPCIONES_SCRIPTS = {}
    
    if not os.path.exists(metadata_path):
        os.makedirs("scripts", exist_ok=True)
        ejemplo_metadata = {
            "1": {
                "nombre": "CSV Cleaner Professional",
                "descripcion": "Cleans CSV files professionally: auto-detects format, repairs broken rows, removes duplicates, preview, and logs. Compatible with large files.",
                "precio": 15
            }
        }
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(ejemplo_metadata, f, indent=2, ensure_ascii=False)
    
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for script_id, info in data.items():
                PRECIOS[script_id] = info.get("precio", 15)
                NOMBRES_SCRIPTS[script_id] = info.get("nombre", f"Script {script_id}")
                DESCRIPCIONES_SCRIPTS[script_id] = info.get("descripcion", "No description")
    except Exception as e:
        print(f"Error loading metadata: {e}")
        PRECIOS = {"1": 15}
        NOMBRES_SCRIPTS = {"1": "CSV Cleaner Professional"}
        DESCRIPCIONES_SCRIPTS = {"1": "Cleans CSV files professionally"}
    
    return PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS

PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS = cargar_scripts_desde_carpeta()