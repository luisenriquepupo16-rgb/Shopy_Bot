# bot.py
# ============================================================
# PUNTO DE ENTRADA PRINCIPAL - EJECUTA ESTE ARCHIVO
# ============================================================

import sys
import os

# Agregar el directorio actual al path (por si acaso)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram.ext import Application, CommandHandler
from config import TOKEN
from handlers import (
    cmd_start, cmd_precio, cmd_comprar, cmd_estado,
    cmd_confirmar, cmd_listar_pagos
)

def main():
    """Función principal que inicia el bot"""
    
    # Verificar que el token esté configurado
    if TOKEN == "1234567890:ABCdefGHIjklmNOPqrstUVwxyz-1234567":
        print("❌ ERROR: No has configurado el TOKEN en config.py")
        print("   Abre config.py y pega el token que te dio BotFather")
        input("Presiona Enter para salir...")
        return
    
    print("🤖 Iniciando bot...")
    print(f"📡 Conectando con Telegram...")
    
    # Crear la aplicación
    app = Application.builder().token(TOKEN).build()
    
    # Registrar comandos públicos
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("precio", cmd_precio))
    app.add_handler(CommandHandler("comprar", cmd_comprar))
    app.add_handler(CommandHandler("estado", cmd_estado))
    
    # Registrar comandos de administrador
    app.add_handler(CommandHandler("confirmar", cmd_confirmar))
    app.add_handler(CommandHandler("lista", cmd_listar_pagos))  # /lista para ver pagos pendientes
    
    # Iniciar el bot
    print("✅ Bot listo y funcionando!")
    print("   Presiona Ctrl+C para detener el bot")
    print("-" * 40)
    
    # Iniciar polling (escuchar mensajes)
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot detenido manualmente.")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        input("Presiona Enter para salir...")