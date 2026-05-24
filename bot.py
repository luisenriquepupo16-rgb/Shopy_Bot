# bot.py
# ============================================================
# PUNTO DE ENTRADA PRINCIPAL - VERSIÓN 2.0 CON IDIOMAS
# ============================================================

import sys
import os
import asyncio
import logging
import time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram.ext import Application, CommandHandler
from telegram.error import TimedOut, NetworkError, Conflict
from config import TOKEN, MI_USER_ID
from handlers import (
    cmd_start, cmd_price, cmd_buy, cmd_status,
    cmd_confirm, cmd_list, cmd_language, verificar_pagos_automaticos
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
    
    logger.info("Registrando comandos...")
    
    app.add_handler(CommandHandler("start", cmd_start))
    logger.info("  ✓ /start registrado")
    
    app.add_handler(CommandHandler("price", cmd_price))
    logger.info("  ✓ /price registrado")
    
    app.add_handler(CommandHandler("buy", cmd_buy))
    logger.info("  ✓ /buy registrado")
    
    app.add_handler(CommandHandler("status", cmd_status))
    logger.info("  ✓ /status registrado")
    
    app.add_handler(CommandHandler("confirm", cmd_confirm))
    logger.info("  ✓ /confirm registrado (admin)")
    
    app.add_handler(CommandHandler("list", cmd_list))
    logger.info("  ✓ /list registrado (admin)")
    
    app.add_handler(CommandHandler("language", cmd_language))
    logger.info("  ✓ /language registrado")
    
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
        
        # Tarea periódica: verificar pagos cada 30 segundos
        job_queue = app.job_queue
        if job_queue:
            job_queue.run_repeating(verificar_pagos_automaticos, interval=30, first=10)
            logger.info("🔄 Verificación automática de pagos activada (cada 30 segundos)")
        else:
            logger.warning("⚠️ JobQueue no disponible - verificación automática desactivada")
        
        # Notificación de inicio al admin
        try:
            await app.bot.send_message(
                chat_id=MI_USER_ID,
                text=(
                    "✅ *Bot iniciado correctamente*\n\n"
                    "🔌 Conectado a Telegram\n"
                    "📍 Railway activo\n"
                    f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    "🟢 Listo para recibir comandos.\n"
                    "🔄 Verificación automática de pagos: ACTIVADA\n"
                    "🌐 Idioma por defecto: Inglés (usa /language para Español)"
                ),
                parse_mode="Markdown"
            )
            logger.info("📨 Notificación de inicio enviada al admin")
        except Exception as e:
            logger.warning(f"No se pudo enviar notificación de inicio: {e}")
        
        logger.info("💡 Presiona Ctrl+C para detener")
        
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