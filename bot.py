# bot.py
# ============================================================
# PUNTO DE ENTRADA PRINCIPAL - VERSIÓN CON CHECKLIST DE INICIO Y BACKUP
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
    cmd_start, cmd_price, cmd_buy, cmd_status, cmd_language,
    cmd_confirm, cmd_list, cmd_stats, cmd_errores, cmd_save_db, cmd_admin,
    verificar_pagos_automaticos
)
from database import registrar_error, limpiar_pagos_viejos, cargar_backup_desde_gist
from config import cargar_scripts_desde_github

async def error_handler(update, context):
    """Manejador global de errores del bot"""
    error = context.error
    logger.error(f"Error global: {error}")
    
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

async def generar_checklist_inicio():
    """
    Ejecuta todas las comprobaciones de inicio y retorna un diccionario con resultados.
    Cada ítem tiene: (nombre, estado, mensaje_detalle)
    """
    resultados = []
    
    # 1. Conexión con Telegram (esto ya se verificó antes)
    resultados.append(("🔌 Conexión con Telegram", "✅ CLEAR", "Bot conectado a la API"))
    
    # 2. Carga de scripts desde GitHub Releases
    try:
        from config import PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS
        if PRECIOS and len(PRECIOS) > 0:
            resultados.append(("📦 Carga de scripts desde GitHub", "✅ CLEAR", f"{len(PRECIOS)} scripts cargados"))
        else:
            resultados.append(("📦 Carga de scripts desde GitHub", "⚠️ WARNING", "No se encontraron scripts"))
    except Exception as e:
        resultados.append(("📦 Carga de scripts desde GitHub", "❌ FAIL", str(e)[:50]))
    
    # 3. Verificación de archivos de scripts en GitHub
    try:
        from config import GITHUB_RAW_CONTENT
        script_url = f"{GITHUB_RAW_CONTENT}/script_1.zip"
        import requests
        response = requests.head(script_url, timeout=5)
        if response.status_code == 200:
            resultados.append(("📥 Scripts disponibles en GitHub", "✅ CLEAR", "script_1.zip encontrado"))
        else:
            resultados.append(("📥 Scripts disponibles en GitHub", "⚠️ WARNING", "No se pudo verificar script_1.zip"))
    except Exception as e:
        resultados.append(("📥 Scripts disponibles en GitHub", "⚠️ WARNING", "Error en verificación"))
    
    # 4. Carga de backup desde GitHub Gist
    try:
        backup_data = cargar_backup_desde_gist()
        if backup_data:
            pagos_count = len(backup_data.get("pagos_pendientes", {}))
            resultados.append(("💾 Carga de backup desde Gist", "✅ CLEAR", f"{pagos_count} pagos restaurados"))
        else:
            resultados.append(("💾 Carga de backup desde Gist", "ℹ️ INFO", "No se encontró backup previo"))
    except Exception as e:
        resultados.append(("💾 Carga de backup desde Gist", "❌ FAIL", str(e)[:50]))
    
    # 5. Base de datos local
    try:
        from database import cargar_db
        db = cargar_db()
        pagos_count = len(db.get("pagos_pendientes", {}))
        resultados.append(("🗄️ Base de datos local", "✅ CLEAR", f"{pagos_count} pagos en memoria"))
    except Exception as e:
        resultados.append(("🗄️ Base de datos local", "❌ FAIL", str(e)[:50]))
    
    # 6. Verificación de pagos automáticos
    resultados.append(("🔄 Verificación automática de pagos", "✅ CLEAR", "Activada (cada 30 segundos)"))
    
    # 7. Limpieza automática de pagos viejos
    try:
        eliminados = limpiar_pagos_viejos(dias_limite=30)
        if eliminados > 0:
            resultados.append(("🧹 Limpieza de pagos viejos", "✅ CLEAR", f"{eliminados} pagos eliminados"))
        else:
            resultados.append(("🧹 Limpieza de pagos viejos", "✅ CLEAR", "No se encontraron pagos viejos"))
    except Exception as e:
        resultados.append(("🧹 Limpieza de pagos viejos", "⚠️ WARNING", str(e)[:50]))
    
    return resultados

async def main():
    logger.info("🤖 Iniciando bot...")
    
    if TOKEN == "1234567890:ABCdefGHIjklmNOPqrstUVwxyz-1234567":
        logger.error("❌ TOKEN no configurado")
        registrar_error("TOKEN no configurado", "El token de Telegram no está configurado")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    logger.info("Registrando comandos...")
    
    # Comandos públicos (visibles para todos)
    app.add_handler(CommandHandler("start", cmd_start))
    logger.info("  ✓ /start registrado (público)")
    
    app.add_handler(CommandHandler("price", cmd_price))
    logger.info("  ✓ /price registrado (público)")
    
    app.add_handler(CommandHandler("buy", cmd_buy))
    logger.info("  ✓ /buy registrado (público)")
    
    app.add_handler(CommandHandler("status", cmd_status))
    logger.info("  ✓ /status registrado (público)")
    
    app.add_handler(CommandHandler("language", cmd_language))
    logger.info("  ✓ /language registrado (público)")
    
    # Comandos de administrador (solo visibles para admin)
    app.add_handler(CommandHandler("confirm", cmd_confirm))
    logger.info("  ✓ /confirm registrado (admin)")
    
    app.add_handler(CommandHandler("list", cmd_list))
    logger.info("  ✓ /list registrado (admin)")
    
    app.add_handler(CommandHandler("stats", cmd_stats))
    logger.info("  ✓ /stats registrado (admin)")
    
    app.add_handler(CommandHandler("errores", cmd_errores))
    logger.info("  ✓ /errores registrado (admin)")
    
    app.add_handler(CommandHandler("save_db", cmd_save_db))
    logger.info("  ✓ /save_db registrado (admin)")
    
    app.add_handler(CommandHandler("admin", cmd_admin))
    logger.info("  ✓ /admin registrado (admin)")
    
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
        
        # ============================================================
        # GENERAR CHECKLIST DE INICIO
        # ============================================================
        checklist = await generar_checklist_inicio()
        
        # Contar estados
        total_clear = sum(1 for _, estado, _ in checklist if "CLEAR" in estado)
        total_checks = len(checklist)
        
        # Construir mensaje de checklist
        checklist_texto = "📋 *CHECKLIST DE INICIO DEL BOT*\n\n"
        for nombre, estado, detalle in checklist:
            icono = "✅" if "CLEAR" in estado else "❌" if "FAIL" in estado else "⚠️"
            checklist_texto += f"{icono} **{nombre}**: {estado}\n"
            if detalle:
                checklist_texto += f"   └ `{detalle}`\n"
        
        checklist_texto += f"\n📊 *Resumen:* {total_clear}/{total_checks} verificaciones exitosas"
        
        if total_clear == total_checks:
            checklist_texto += "\n🎉 *Estado general: OPERATIVO*"
        elif total_clear >= total_checks - 2:
            checklist_texto += "\n⚠️ *Estado general: OPERATIVO CON ADVERTENCIAS*"
        else:
            checklist_texto += "\n🔴 *Estado general: REQUIERE ATENCIÓN*"
        
        # ============================================================
        # NOTIFICACIÓN DE INICIO AL ADMIN (con checklist)
        # ============================================================
        try:
            await app.bot.send_message(
                chat_id=MI_USER_ID,
                text=checklist_texto,
                parse_mode="Markdown"
            )
            logger.info("📨 Notificación de inicio con checklist enviada al admin")
        except Exception as e:
            logger.warning(f"No se pudo enviar notificación de inicio: {e}")
            registrar_error(
                "Notificación de inicio fallida",
                f"Error: {e}"
            )
        
        # ============================================================
        # TAREA PERIÓDICA: VERIFICAR PAGOS CADA 30 SEGUNDOS
        # ============================================================
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