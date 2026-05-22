# app.py - Punto de entrada para Render
import os
import threading
from flask import Flask, request, jsonify
from bot import main as run_bot

# Crear aplicación Flask para health checks
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Bot is running"}), 200

# Iniciar el bot de Telegram en un hilo separado
def start_telegram_bot():
    run_bot()

if __name__ == "__main__":
    # Iniciar el bot en segundo plano
    bot_thread = threading.Thread(target=start_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Iniciar servidor Flask (obligatorio para Render)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)