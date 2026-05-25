# handlers/admin.py
import asyncio
import io
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    NOMBRES_SCRIPTS, MI_USER_ID,
    descargar_script_desde_github
)
from database import (
    cargar_db, obtener_pago, actualizar_estado_pago,
    obtener_ultimos_errores, guardar_backup_en_gist
)
from .textos import get_text

logger = logging.getLogger(__name__)

async def cmd_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        text = get_text(user_id, "confirm_not_authorized")
        await update.message.reply_text(text)
        return
    
    args = context.args
    if not args:
        text = get_text(user_id, "confirm_usage")
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    pago_id = args[0]
    pago = obtener_pago(pago_id)
    
    if not pago:
        text = get_text(user_id, "confirm_not_found", pago_id=pago_id)
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    if pago["estado"] != "pendiente" and pago["estado"] != "pagado":
        text = get_text(user_id, "confirm_already_processed", estado=pago["estado"])
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    script_id = pago["script_id"]
    comprador_id = pago["user_id"]
    
    await update.message.reply_text("📤 Descargando script desde GitHub...")
    
    script_content = descargar_script_desde_github(script_id)
    
    if not script_content:
        text = get_text(user_id, "confirm_file_not_found")
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    max_intentos = 3
    intento = 1
    enviado = False
    ultimo_error = None
    
    while intento <= max_intentos and not enviado:
        try:
            await context.bot.send_document(
                chat_id=comprador_id,
                document=io.BytesIO(script_content),
                filename=f"script_{script_id}.zip",
                caption=f"🎉 Thank you for your purchase!\n\nScript: {NOMBRES_SCRIPTS.get(script_id, 'Unknown')}\n\nNo support included."
            )
            enviado = True
            logger.info(f"Script {script_id} enviado a {comprador_id} en intento {intento}")
            
        except Exception as e:
            ultimo_error = e
            logger.warning(f"Intento {intento} fallido para {comprador_id}: {e}")
            
            if intento < max_intentos:
                await asyncio.sleep(2 * intento)
            intento += 1
    
    if enviado:
        if actualizar_estado_pago(pago_id, "entregado"):
            text = get_text(user_id, "confirm_sent", comprador_id=comprador_id)
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            text = get_text(user_id, "confirm_db_error")
            await update.message.reply_text(text, parse_mode="Markdown")
    else:
        text = get_text(user_id, "confirm_send_error", error=str(ultimo_error)[:200])
        await update.message.reply_text(text, parse_mode="Markdown")
        logger.error(f"No se pudo enviar script {script_id} a {comprador_id} después de {max_intentos} intentos")

async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        text = get_text(user_id, "list_not_authorized")
        await update.message.reply_text(text)
        return
    
    db = cargar_db()
    pagos_pendientes = db.get("pagos_pendientes", {})
    
    if not pagos_pendientes:
        text = get_text(user_id, "list_empty")
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    mensaje = get_text(user_id, "list_title")
    for pago_id, datos in pagos_pendientes.items():
        if datos["estado"] == "pendiente":
            mensaje += get_text(user_id, "list_item",
                               pago_id=pago_id,
                               script_id=datos["script_id"],
                               monto=datos["monto"],
                               user_id=datos["user_id"])
    
    mensaje += get_text(user_id, "list_footer")
    await update.message.reply_text(mensaje, parse_mode="Markdown")

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        await update.message.reply_text("❌ Not authorized.")
        return
    
    from database import obtener_estadisticas
    
    stats = obtener_estadisticas()
    
    total_compras = stats["total_compras"]
    total_ganado = stats["total_ganado"]
    scripts_ordenados = stats["scripts_ordenados"]
    
    mensaje = "📊 *BOT STATISTICS*\n\n"
    mensaje += f"💰 *Total earned:* {total_ganado:.2f} USDT\n"
    mensaje += f"📦 *Total purchases:* {total_compras}\n"
    mensaje += f"⭐ *Average per sale:* {total_ganado/total_compras if total_compras > 0 else 0:.2f} USDT\n\n"
    
    mensaje += "📋 *Top scripts:*\n"
    if scripts_ordenados:
        for script_id, cantidad in scripts_ordenados:
            nombre = NOMBRES_SCRIPTS.get(script_id, f"Script {script_id}")
            mensaje += f"   {script_id}. {nombre}: {cantidad} sale(s)\n"
    else:
        mensaje += "   No sales recorded yet.\n"
    
    mensaje += "\n🟢 *Status:* Active on Railway"
    await update.message.reply_text(mensaje, parse_mode="Markdown")

async def cmd_errores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        await update.message.reply_text("❌ No autorizado.")
        return
    
    logs = obtener_ultimos_errores(50)
    text = get_text(user_id, "errors_title")
    
    if len(text + logs) > 4000:
        logs = logs[-4000:]
    
    if logs and logs.strip():
        await update.message.reply_text(
            f"{text}```\n{logs}\n```",
            parse_mode="Markdown"
        )
    else:
        empty_text = get_text(user_id, "errors_empty")
        await update.message.reply_text(empty_text, parse_mode="Markdown")

async def cmd_save_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        await update.message.reply_text("❌ No autorizado.")
        return
    
    await update.message.reply_text(get_text(user_id, "save_db_start"))
    
    db = cargar_db()
    
    if guardar_backup_en_gist(db):
        await update.message.reply_text(
            get_text(user_id, "save_db_success"),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            get_text(user_id, "save_db_error"),
            parse_mode="Markdown"
        )


# ============================================================
# COMANDO PARA VER COMANDOS DE ADMIN (solo admin)
# ============================================================

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        await update.message.reply_text("❌ No autorizado.")
        return
    
    mensaje = (
        "👑 *Panel de Administración*\n\n"
        "📌 *Comandos disponibles para admin:*\n\n"
        "/confirm [ID_pago] - Confirmar pago y entregar script\n"
        "/list - Ver pagos pendientes\n"
        "/stats - Ver estadísticas del bot\n"
        "/errores - Ver últimos errores registrados\n"
        "/save_db - Guardar backup manual de la base de datos\n"
        "/admin - Mostrar este panel\n\n"
        "📊 *Comandos públicos (visibles para usuarios):*\n"
        "/start, /price, /buy, /status, /language\n\n"
        "🟢 *Estado:* Activo"
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")