# bot.py
# ============================================================
# PUNTO DE ENTRADA PRINCIPAL - VERSIÓN CON LOG DE ERRORES, ESTADÍSTICAS Y LIMPIEZA AUTOMÁTICA
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
    cmd_confirm, cmd_list, cmd_language, cmd_errores, cmd_stats,
    verificar_pagos_automaticos
)
from database import registrar_error, limpiar_pagos_viejos

async def error_handler(update, context):
    """Manejador global de errores del bot"""
    error = context.error
    logger.error(f"Error global: {error}")
    
    # Registrar en archivo de errores
    registrar_error(
        f"Error global en bot",
        f"Update: {update} | Error: {error}"
    )
    
    if isinstance(error, Conflict):
        logger.critical("Conflicto: otro bot con el mismo token está corriendo")
        registrar_error(
            "Conflicto de instancia",
            f"Token: {TOKEN[:15]}..."
        )
    elif isinstance(error, TimedOut):
        logger.warning("Timeout en conexión con Telegram")
        registrar_error(
            "Timeout en conexión",
            "La conexión con Telegram excedió el tiempo de espera"
        )
    elif isinstance(error, NetworkError):
        logger.warning("Error de red")
        registrar_error(
            "Error de red",
            f"Detalle: {error}"
        )

async def main():
    logger.info("🤖 Iniciando bot...")
    
    if TOKEN == "1234567890:ABCdefGHIjklmNOPqrstUVwxyz-1234567":
        logger.error("❌ TOKEN no configurado")
        registrar_error("TOKEN no configurado", "El token de Telegram no está configurado")
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
    
    app.add_handler(CommandHandler("errores", cmd_errores))
    logger.info("  ✓ /errores registrado (admin)")
    
    app.add_handler(CommandHandler("stats", cmd_stats))
    logger.info("  ✓ /stats registrado (admin)")
    
    # Manejador global de errores
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
            registrar_error(
                "JobQueue no disponible",
                "La verificación automática de pagos está desactivada"
            )
        
        # ============================================================
        # LIMPIEZA AUTOMÁTICA DE PAGOS VIEJOS (al iniciar)
        # ============================================================
        try:
            eliminados = limpiar_pagos_viejos(dias_limite=30)
            if eliminados > 0:
                logger.info(f"🧹 Limpieza automática: {eliminados} pagos viejos eliminados")
                await app.bot.send_message(
                    chat_id=MI_USER_ID,
                    text=f"🧹 *Limpieza automática*\n\nSe eliminaron {eliminados} pagos pendientes con más de 30 días de antigüedad.\n\n✅ Base de datos optimizada.",
                    parse_mode="Markdown"
                )
            else:
                logger.info("🧹 Limpieza automática: No se encontraron pagos viejos")
        except Exception as e:
            logger.warning(f"Error en limpieza automática: {e}")
            registrar_error(
                "Limpieza automática fallida",
                f"Error: {e}"
            )
        
        # ============================================================
        # NOTIFICACIÓN DE INICIO AL ADMIN
        # ============================================================
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
                    "🌐 Idioma por defecto: Inglés (usa /language para Español)\n"
                    "📋 Para ver errores: /errores\n"
                    "📊 Para ver estadísticas: /stats\n"
                    "🧹 Limpieza automática de pagos viejos: ACTIVADA (30 días)"
                ),
                parse_mode="Markdown"
            )
            logger.info("📨 Notificación de inicio enviada al admin")
        except Exception as e:
            logger.warning(f"No se pudo enviar notificación de inicio: {e}")
            registrar_error(
                "Notificación de inicio fallida",
                f"Error: {e}"
            )
        
        logger.info("💡 Presiona Ctrl+C para detener")
        
        while True:
            await asyncio.sleep(1)
            
    except Conflict:
        logger.critical("❌ Conflicto: Ya hay otra instancia del bot corriendo")
        registrar_error(
            "Conflicto de instancia",
            "Ya hay otra instancia del bot corriendo con el mismo token"
        )
    except Exception as e:
        logger.exception(f"❌ Error fatal: {e}")
        registrar_error(
            "Error fatal en main",
            f"Error: {e}"
        )
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
        registrar_error(
            "Error en ejecución principal",
            f"Error: {e}"
        )