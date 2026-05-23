# bot.py
# ============================================================
# PUNTO DE ENTRADA PRINCIPAL CON RECONEXIÓN ROBUSTA
# ============================================================

import sys
import os
import asyncio
import logging

# Configurar logging para ver errores detallados
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram.ext import Application, CommandHandler
from telegram.error import TimedOut, NetworkError, Conflict
from config import TOKEN
from handlers import (
    cmd_start, cmd_precio, cmd_comprar, cmd_estado,
    cmd_confirmar, cmd_listar_pagos
)

async def error_handler(update, context):
    """Maneja errores globales del bot"""
    error = context.error
    logger.error(f"Error: {error}")
    
    # Si es error de conexión, no hacer nada (el bot reintentará solo)
    if isinstance(error, (TimedOut, NetworkError)):
        logger.warning("Error de red, reintentando...")
    elif isinstance(error, Conflict):
        logger.critical("Conflicto: otro bot con el mismo token está corriendo")
    else:
        logger.exception("Error no manejado")

async def main():
    """Función principal con reconexión automática"""
    
    logger.info("🤖 Iniciando bot...")
    
    if TOKEN == "1234567890:ABCdefGHIjklmNOPqrstUVwxyz-1234567":
        logger.error("❌ TOKEN no configurado en config.py")
        return
    
    # Crear aplicación
    app = Application.builder().token(TOKEN).build()
    
    # Registrar comandos
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("precio", cmd_precio))
    app.add_handler(CommandHandler("comprar", cmd_comprar))
    app.add_handler(CommandHandler("estado", cmd_estado))
    app.add_handler(CommandHandler("confirmar", cmd_confirmar))
    app.add_handler(CommandHandler("lista", cmd_listar_pagos))
    
    # Registrar manejador de errores global
    app.add_error_handler(error_handler)
    
    logger.info("✅ Handlers registrados")
    logger.info("🔄 Conectando con Telegram...")
    
    # Iniciar polling con parámetros para red inestable
    try:
        # Usar run_polling con timeout y read_timeout explícitos
        await app.initialize()
        await app.start()
        
        # Iniciar polling con reintentos automáticos
        await app.updater.start_polling(
            poll_interval=1.0,
            timeout=10,
            drop_pending_updates=True
        )
        
        logger.info("✅ Bot conectado y funcionando!")
        logger.info("💡 Presiona Ctrl+C para detener")
        
        # Mantener vivo
        while True:
            await asyncio.sleep(1)
            
    except Conflict:
        logger.critical("❌ Conflicto: Ya hay otra instancia del bot corriendo con este token")
        logger.info("Solución: Detén la otra instancia o genera un nuevo token en BotFather")
    except Exception as e:
        logger.exception(f"❌ Error fatal: {e}")
        logger.info("Reintentando en 10 segundos...")
        await asyncio.sleep(10)
        # Reintentar la conexión
        return await main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot detenido manualmente")
    except Exception as e:
        logger.error(f"Error en main: {e}")r...")