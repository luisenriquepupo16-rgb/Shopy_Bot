# config.py
# ============================================================
# CONFIGURACIÓN DEL BOT - CAMBIA SOLO LO QUE ESTÁ INDICADO
# ============================================================

# TOKEN de BotFather (CÁMBIALO por el tuyo)
TOKEN = "8907545202:AAFH1we_J12zJhjDx1tCCZHddkLKT8x8naw" # <-- CAMBIA ESTO

# Tu ID de usuario de Telegram (CÁMBIALO por el tuyo)
# Cómo obtenerlo: Habla con @userinfobot en Telegram, te enviará tu ID
MI_USER_ID = 6985343427  # <-- CAMBIA ESTO

# Precios de los scripts (en USDT)
# Formato: "ID_del_script": precio
PRECIOS = {
    "1": 10,   # Descargador de YouTube MP3
    "2": 15,   # Limpiador de CSV
    "3": 8,    # Monitor de precios cripto
}

# Nombres descriptivos de los scripts (para mostrar en /precio)
NOMBRES_SCRIPTS = {
    "1": "🎵 Descargador de YouTube MP3",
    "2": "🧹 Limpiador de CSV",
    "3": "📊 Monitor de precios cripto",
}

DESCRIPCIONES_SCRIPTS = {
    "1": "Convierte videos de YouTube a MP3 por línea de comandos. Sin interfaz gráfica, ideal para automatización.",
    "2": "Limpia y normaliza archivos CSV duplicados o con errores. Funciona desde terminal.",
    "3": "Monitorea precios de 10+ criptomonedas en tiempo real desde la consola.",
}

# Tu dirección de wallet USDT (TRC-20) - Cámbiala por la tuya
WALLET_DIRECCION = "TU_DIRECCION_USDT_TRC20_AQUI"  # <-- CAMBIA ESTO

# Mensaje que se muestra al comprar (instrucciones de pago)
MENSAJE_PAGO = """
💰 *Instrucciones de pago:*

1. Abre tu wallet que soporte USDT (TronLink, Binance, etc.)
2. Envía el monto exacto a esta dirección:
   `{direccion}`
3. Usa la red *TRC-20* (importante, no uses otra red)
4. Una vez enviado, usa /estado {pago_id} para verificar

⚠️ El script se enviará automáticamente cuando confirme el pago manualmente.
"""