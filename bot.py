# bot.py
# ============================================================
# PUNTO DE ENTRADA PRINCIPAL - VERSION 1.2 CON NOTIFICACIÓN AL ADMIN
# ============================================================

import sys
import os
import asyncio
import logging
import time  # <-- AGREGADO para la notificación

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram.ext import Application, CommandHandler
from telegram.error import TimedOut, NetworkError, Conflict
from config import TOKEN, MI_USER_ID  # <-- AGREGADO MI_USER_ID
from handlers import (
    cmd_start, cmd_precio, cmd_comprar, cmd_estado,
    cmd_confirmar, cmd_listar_pagos
    # NOTA: cmd_logs NO está incluido (por ahora)
)

async def error_handler(update, context):
    error = context.error
    logger.error(f"Error global: {error}")
    if isinstance(error, Conflict):
        logger.critical("Conflicto: otro bot con el mismo token está corriendo")

async def main():
    logger.info("🤖 Iniciando bot...")
    
    if TOKEN == "1234567890:ABCdefGHIjklmNOPqrstUVwxyz-1234567":
        logger.error("❌ TOKEN no configurado")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # ============================================================
    # REGISTRO EXPLÍCITO DE COMANDOS
    # ============================================================
    logger.info("Registrando comandos...")
    
    app.add_handler(CommandHandler("start", cmd_start))
    logger.info("  ✓ /start registrado")
    
    app.add_handler(CommandHandler("precio", cmd_precio))
    logger.info("  ✓ /precio registrado")
    
    app.add_handler(CommandHandler("comprar", cmd_comprar))
    logger.info("  ✓ /comprar registrado")
    
    app.add_handler(CommandHandler("estado", cmd_estado))
    logger.info("  ✓ /estado registrado")
    
    app.add_handler(CommandHandler("confirmar", cmd_confirmar))
    logger.info("  ✓ /confirmar registrado (admin)")
    
    app.add_handler(CommandHandler("lista", cmd_listar_pagos))
    logger.info("  ✓ /lista registrado (admin)")
    
    app.add_error_handler(error_handler)
    
    logger.info("✅ Todos los handlers registrados")
    logger.info("🔄 Conectando con Telegram...")
    
    try:
        await app.initialize()
        await app.start()
        
        await app.updater.start_polling(
            poll_interval=1.0,
            timeout=10,
            drop_pending_updates=True
        )
        
        logger.info("✅ Bot conectado y funcionando!")
        
        # ============================================================
        # NOTIFICACIÓN DE INICIO AL ADMIN (TIP #008)
        # ============================================================
        try:
            await app.bot.send_message(
                chat_id=MI_USER_ID,
                text=(
                    "✅ *Bot iniciado correctamente*\n\n"
                    "🔌 Conectado a Telegram\n"
                    "📍 Railway activo\n"
                    f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    "🟢 Listo para recibir comandos."
                ),
                parse_mode="Markdown"
            )
            logger.info("📨 Notificación de inicio enviada al admin")
        except Exception as e:
            logger.warning(f"No se pudo enviar notificación de inicio: {e}")
        
        logger.info("💡 Presiona Ctrl+C para detener")
        
        # Mantener vivo
        while True:
            await asyncio.sleep(1)
            
    except Conflict:
        logger.critical("❌ Conflicto: Ya hay otra instancia del bot corriendo")
    except Exception as e:
        logger.exception(f"❌ Error fatal: {e}")
        logger.info("Reintentando en 10 segundos...")
        await asyncio.sleep(10)
        return await main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot detenido manualmente")
    except Exception as e:
        logger.error(f"Error en main: {e}")