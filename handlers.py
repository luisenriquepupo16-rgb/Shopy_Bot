# handlers.py
# ============================================================
# MANEJADORES DE COMANDOS DEL BOT - VERSIÓN CON REINTENTOS Y LOG DE ERRORES
# ============================================================

import time
import os
import logging
import asyncio
import io
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS,
    WALLET_DIRECCION, MENSAJE_PAGO, MI_USER_ID,
    descargar_script_desde_github
)
from database import (
    cargar_db, guardar_pago, obtener_pago, actualizar_estado_pago,
    limite_compras_por_usuario, verificar_pago_usdt_trc20,
    obtener_idioma_usuario, guardar_idioma_usuario,
    registrar_error, obtener_ultimos_errores
)

logger = logging.getLogger(__name__)

# ============================================================
# TEXTO EN IDIOMAS
# ============================================================

TEXTOS = {
    "en": {
        "start": (
            "🤖 *Script Sales Bot*\n\n"
            "This bot sells automation scripts for command line.\n\n"
            "📌 *Available commands:*\n"
            "/price - View scripts and prices\n"
            "/buy [ID] - Buy a script\n"
            "/status [payment_ID] - Check payment status\n"
            "/language - Change language (Español/English)\n"
            "/errores - View error logs (admin only)\n\n"
            "⚠️ *No customer support.* This bot is fully automated."
        ),
        "price_title": "📋 *Available scripts:*\n\n",
        "price_buy": "\nTo buy: /buy [ID]\nExample: /buy 1",
        "price_id": "ID: {script_id} - {nombre}\n   └ {desc}\n   └ Price: {precio} USDT (TRC-20)\n",
        "buy_error_no_id": "❌ *Error:* Specify script ID.\n\nUsage: /buy [ID]\nExample: /buy 1\n\nUse /price to see available IDs.",
        "buy_error_invalid_id": "❌ *Error:* ID '{script_id}' is not valid.\n\nUse /price to see available scripts.",
        "buy_limit_reached": "❌ *Limit reached*\n\nYou have exceeded the limit of 5 purchases in the last 24 hours.\nPlease wait before making new purchases.",
        "buy_internal_error": "Internal error. Please try again later.",
        "buy_success": (
            "💰 *Purchase request generated*\n\n"
            "📦 Script: {nombre}\n"
            "💵 Amount: {monto} USDT (TRC-20)\n"
            "🆔 *Payment ID:* `{pago_id}`\n\n"
            "{mensaje_pago}\n\n"
            "After paying, use /status {pago_id} to verify."
        ),
        "buy_db_error": "❌ *Internal error:* Could not generate request. Try again later.",
        "buy_technical_error": "❌ *Technical error:* {error}",
        "status_error_no_id": "❌ *Error:* Specify payment ID.\n\nUsage: /status [payment_ID]\nExample: /status 123456789_1732123456",
        "status_error_not_found": "❌ *Error:* No payment found with ID `{pago_id}`.\n\nCheck the ID and try again.",
        "status_pending": "⏳ *Status: Pending*\n\n📦 Script: {nombre}\n💵 Amount: {monto} USDT\n\nPayment not yet confirmed.",
        "status_paid": "✅ *Status: Paid (awaiting delivery)*\n\n📦 Script: {nombre}\n\nPayment confirmed. You will receive the script shortly.",
        "status_delivered": "🎉 *Status: Delivered*\n\n📦 Script: {nombre}\n\nThe script has been sent to this chat.",
        "status_unknown": "📌 *Status:* {estado}",
        "confirm_not_authorized": "❌ Not authorized.",
        "confirm_usage": "📌 *Usage:* /confirm [payment_ID]\n\nExample: /confirm 123456789_1732123456",
        "confirm_not_found": "❌ *Error:* Payment `{pago_id}` not found.",
        "confirm_already_processed": "⚠️ This payment was already processed. Status: {estado}",
        "confirm_file_not_found": "❌ *Error:* Script file not found in GitHub Release",
        "confirm_sent": "✅ Script sent successfully to {comprador_id}",
        "confirm_db_error": "⚠️ Script sent but database not updated",
        "confirm_send_error": "❌ *Error sending:* {error}",
        "list_not_authorized": "❌ Not authorized.",
        "list_empty": "📭 No pending payments.",
        "list_title": "📋 *Pending payments:*\n\n",
        "list_item": "🆔 `{pago_id}`\n   └ Script: {script_id} | Amount: {monto} USDT\n   └ User: {user_id}\n",
        "list_footer": "\nTo confirm: /confirm [payment_ID]",
        "language_changed": "✅ *Language changed to Spanish.*\n\nUse /language to switch back to English.",
        "language_changed_en": "✅ *Language changed to English.*\n\nUse /language to switch to Spanish.",
        "payment_detected": "✅ *Payment detected automatically!*\n\nID: {pago_id}\nAmount: {monto} USDT\nTx: {tx_id}...\n\nUse /confirm {pago_id} to deliver the script.",
        "errors_empty": "✅ No errors registered in the system.",
        "errors_title": "📋 *Last errors registered:*\n\n"
    },
    "es": {
        "start": (
            "🤖 *Bot de Venta de Scripts*\n\n"
            "Este bot vende scripts de automatización por línea de comandos.\n\n"
            "📌 *Comandos disponibles:*\n"
            "/price - Ver scripts y precios\n"
            "/buy [ID] - Comprar un script\n"
            "/status [ID_pago] - Verificar estado de pago\n"
            "/language - Cambiar idioma (Español/English)\n"
            "/errores - Ver errores (solo admin)\n\n"
            "⚠️ *No hay atención al cliente.* Este bot es completamente automático."
        ),
        "price_title": "📋 *Scripts disponibles:*\n\n",
        "price_buy": "\nPara comprar: /buy [ID]\nEjemplo: /buy 1",
        "price_id": "ID: {script_id} - {nombre}\n   └ {desc}\n   └ Precio: {precio} USDT (TRC-20)\n",
        "buy_error_no_id": "❌ *Error:* Especifica el ID del script.\n\nUso: /buy [ID]\nEjemplo: /buy 1\n\nUsa /price para ver los IDs disponibles.",
        "buy_error_invalid_id": "❌ *Error:* El ID '{script_id}' no es válido.\n\nUsa /price para ver los scripts disponibles.",
        "buy_limit_reached": "❌ *Límite alcanzado*\n\nHas superado el límite de 5 compras en las últimas 24 horas.\nPor favor, espera antes de realizar nuevas compras.",
        "buy_internal_error": "Error interno. Intenta de nuevo más tarde.",
        "buy_success": (
            "💰 *Solicitud de compra generada*\n\n"
            "📦 Script: {nombre}\n"
            "💵 Monto: {monto} USDT (TRC-20)\n"
            "🆔 *ID de pago:* `{pago_id}`\n\n"
            "{mensaje_pago}\n\n"
            "Después de pagar, usa /status {pago_id} para verificar."
        ),
        "buy_db_error": "❌ *Error interno:* No se pudo generar la solicitud. Intenta de nuevo más tarde.",
        "buy_technical_error": "❌ *Error técnico:* {error}",
        "status_error_no_id": "❌ *Error:* Especifica el ID de pago.\n\nUso: /status [ID_pago]\nEjemplo: /status 123456789_1732123456",
        "status_error_not_found": "❌ *Error:* No se encontró ningún pago con ID `{pago_id}`.\n\nVerifica el ID e intenta de nuevo.",
        "status_pending": "⏳ *Estado: Pendiente*\n\n📦 Script: {nombre}\n💵 Monto: {monto} USDT\n\nAún no se ha confirmado el pago.",
        "status_paid": "✅ *Estado: Pagado (esperando entrega)*\n\n📦 Script: {nombre}\n\nEl pago ha sido confirmado. En breve recibirás el script.",
        "status_delivered": "🎉 *Estado: Entregado*\n\n📦 Script: {nombre}\n\nEl script ya fue enviado a este chat.",
        "status_unknown": "📌 *Estado:* {estado}",
        "confirm_not_authorized": "❌ No autorizado.",
        "confirm_usage": "📌 *Uso:* /confirm [ID_pago]\n\nEjemplo: /confirm 123456789_1732123456",
        "confirm_not_found": "❌ *Error:* No se encontró el pago `{pago_id}`.",
        "confirm_already_processed": "⚠️ Este pago ya fue procesado. Estado: {estado}",
        "confirm_file_not_found": "❌ *Error:* No se encontró el archivo del script en GitHub Release",
        "confirm_sent": "✅ Script enviado correctamente a {comprador_id}",
        "confirm_db_error": "⚠️ Script enviado pero no se actualizó la base de datos",
        "confirm_send_error": "❌ *Error al enviar:* {error}",
        "list_not_authorized": "❌ No autorizado.",
        "list_empty": "📭 No hay pagos pendientes.",
        "list_title": "📋 *Pagos pendientes:*\n\n",
        "list_item": "🆔 `{pago_id}`\n   └ Script: {script_id} | Monto: {monto} USDT\n   └ Usuario: {user_id}\n",
        "list_footer": "\nPara confirmar: /confirm [ID_pago]",
        "language_changed": "✅ *Idioma cambiado a Inglés.*\n\nUsa /language para volver a Español.",
        "language_changed_en": "✅ *Language changed to English.*\n\nUse /language to switch to Spanish.",
        "payment_detected": "✅ *¡Pago detectado automáticamente!*\n\nID: {pago_id}\nMonto: {monto} USDT\nTx: {tx_id}...\n\nUsa /confirm {pago_id} para entregar el script.",
        "errors_empty": "✅ No hay errores registrados en el sistema.",
        "errors_title": "📋 *Últimos errores registrados:*\n\n"
    }
}

def get_text(user_id, key, **kwargs):
    """Obtiene el texto en el idioma del usuario"""
    lang = obtener_idioma_usuario(user_id)
    text = TEXTOS.get(lang, TEXTOS["en"]).get(key, TEXTOS["en"][key])
    return text.format(**kwargs) if kwargs else text

# ============================================================
# COMANDOS PÚBLICOS
# ============================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = get_text(user_id, "start")
    await update.message.reply_text(text, parse_mode="Markdown")
    logger.info(f"Usuario {user_id} ejecutó /start")

async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mensaje = get_text(user_id, "price_title")
    
    for script_id, nombre in NOMBRES_SCRIPTS.items():
        precio = PRECIOS.get(script_id, "?")
        desc = DESCRIPCIONES_SCRIPTS.get(script_id, "No description")
        mensaje += get_text(user_id, "price_id", 
                           script_id=script_id, 
                           nombre=nombre, 
                           desc=desc, 
                           precio=precio)
    
    mensaje += get_text(user_id, "price_buy")
    
    await update.message.reply_text(mensaje, parse_mode="Markdown")
    logger.info(f"Usuario {user_id} ejecutó /price")

async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    
    logger.info(f"Usuario {user_id} ejecutó /buy con args: {args}")
    
    if not args:
        text = get_text(user_id, "buy_error_no_id")
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    script_id = args[0]
    logger.info(f"Usuario {user_id} - Script ID solicitado: {script_id}")
    
    if script_id not in PRECIOS:
        text = get_text(user_id, "buy_error_invalid_id", script_id=script_id)
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    try:
        if not limite_compras_por_usuario(user_id, limite=5):
            text = get_text(user_id, "buy_limit_reached")
            await update.message.reply_text(text, parse_mode="Markdown")
            return
    except Exception as e:
        logger.error(f"Error al verificar límite para {user_id}: {e}")
        registrar_error(f"cmd_buy - Límite de compras", f"Usuario {user_id} | Error: {e}")
        text = get_text(user_id, "buy_internal_error")
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    pago_id = f"{user_id}_{int(time.time())}"
    monto = PRECIOS[script_id]
    
    datos_pago = {
        "user_id": user_id,
        "script_id": script_id,
        "monto": monto,
        "estado": "pendiente",
        "fecha": time.time()
    }
    
    logger.info(f"Usuario {user_id} - Generando pago ID: {pago_id}")
    
    try:
        if guardar_pago(pago_id, datos_pago):
            mensaje_pago = MENSAJE_PAGO.format(
                direccion=WALLET_DIRECCION,
                pago_id=pago_id
            )
            
            respuesta = get_text(user_id, "buy_success",
                                nombre=NOMBRES_SCRIPTS[script_id],
                                monto=monto,
                                pago_id=pago_id,
                                mensaje_pago=mensaje_pago)
            
            await update.message.reply_text(respuesta, parse_mode="Markdown")
            logger.info(f"Usuario {user_id} - Respuesta de compra enviada correctamente")
        else:
            logger.error(f"Usuario {user_id} - Error al guardar pago en DB")
            registrar_error(f"cmd_buy - Guardar pago", f"Usuario {user_id} | Script {script_id}")
            text = get_text(user_id, "buy_db_error")
            await update.message.reply_text(text, parse_mode="Markdown")
    
    except Exception as e:
        logger.error(f"Usuario {user_id} - Excepción en cmd_buy: {e}")
        registrar_error(f"cmd_buy - Excepción", f"Usuario {user_id} | Error: {e}")
        text = get_text(user_id, "buy_technical_error", error=str(e)[:100])
        await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        text = get_text(user_id, "status_error_no_id")
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    pago_id = args[0]
    pago = obtener_pago(pago_id)
    
    if not pago:
        text = get_text(user_id, "status_error_not_found", pago_id=pago_id)
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    estado = pago["estado"]
    script_id = pago["script_id"]
    monto = pago["monto"]
    
    if estado == "pendiente":
        text = get_text(user_id, "status_pending", 
                       nombre=NOMBRES_SCRIPTS.get(script_id, "Unknown"),
                       monto=monto)
    elif estado == "pagado":
        text = get_text(user_id, "status_paid",
                       nombre=NOMBRES_SCRIPTS.get(script_id, "Unknown"))
    elif estado == "entregado":
        text = get_text(user_id, "status_delivered",
                       nombre=NOMBRES_SCRIPTS.get(script_id, "Unknown"))
    else:
        text = get_text(user_id, "status_unknown", estado=estado)
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_actual = obtener_idioma_usuario(user_id)
    
    if lang_actual == "en":
        guardar_idioma_usuario(user_id, "es")
        text = "✅ *Idioma cambiado a Español.*\n\nUsa /language para volver a Inglés."
    else:
        guardar_idioma_usuario(user_id, "en")
        text = "✅ *Language changed to English.*\n\nUse /language to switch to Spanish."
    
    await update.message.reply_text(text, parse_mode="Markdown")
    logger.info(f"Usuario {user_id} cambió idioma a {'es' if lang_actual == 'en' else 'en'}")

# ============================================================
# COMANDO PARA VER ERRORES (solo admin)
# ============================================================

async def cmd_errores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        await update.message.reply_text("❌ No autorizado.")
        return
    
    logs = obtener_ultimos_errores(50)
    text = get_text(user_id, "errors_title")
    
    if len(text + logs) > 4000:
        logs = logs[-4000:]  # Limitar a 4000 caracteres para Telegram
    
    if logs and logs.strip():
        await update.message.reply_text(
            f"{text}```\n{logs}\n```",
            parse_mode="Markdown"
        )
    else:
        empty_text = get_text(user_id, "errors_empty")
        await update.message.reply_text(empty_text, parse_mode="Markdown")

# ============================================================
# COMANDOS DE ADMINISTRADOR
# ============================================================

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
    
    # Descargar script desde GitHub Releases
    script_content = descargar_script_desde_github(script_id)
    
    if not script_content:
        registrar_error(f"cmd_confirm - Script no encontrado", f"Script ID: {script_id}")
        text = get_text(user_id, "confirm_file_not_found")
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    
    # ============================================================
    # REINTENTAR ENVÍO HASTA 3 VECES
    # ============================================================
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
            registrar_error(f"cmd_confirm - Intento {intento} fallido", f"Comprador: {comprador_id} | Error: {e}")
            
            if intento < max_intentos:
                # Esperar antes de reintentar (2 segundos por intento)
                await asyncio.sleep(2 * intento)
            intento += 1
    
    # ============================================================
    # PROCESAR RESULTADO DEL ENVÍO
    # ============================================================
    if enviado:
        if actualizar_estado_pago(pago_id, "entregado"):
            text = get_text(user_id, "confirm_sent", comprador_id=comprador_id)
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            registrar_error(f"cmd_confirm - DB no actualizada", f"Pago ID: {pago_id}")
            text = get_text(user_id, "confirm_db_error")
            await update.message.reply_text(text, parse_mode="Markdown")
    else:
        registrar_error(f"cmd_confirm - Envío fallido tras {max_intentos} intentos", f"Comprador: {comprador_id} | Script: {script_id}")
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



# ============================================================
# COMANDO PARA ESTADÍSTICAS (solo admin)
# ============================================================

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



# ============================================================
# TAREA PERIÓDICA PARA VERIFICAR PAGOS AUTOMÁTICAMENTE
# ============================================================

async def verificar_pagos_automaticos(context: ContextTypes.DEFAULT_TYPE):
    db = cargar_db()
    
    for pago_id, datos in db["pagos_pendientes"].items():
        if datos["estado"] != "pendiente":
            continue
        
        monto = datos["monto"]
        
        pago = verificar_pago_usdt_trc20(WALLET_DIRECCION, monto, timeout_minutos=60)
        
        if pago:
            actualizar_estado_pago(pago_id, "pagado")
            
            text = TEXTOS["en"]["payment_detected"].format(
                pago_id=pago_id,
                monto=monto,
                tx_id=pago["tx_id"][:10]
            )
            
            try:
                await context.bot.send_message(
                    chat_id=MI_USER_ID,
                    text=text,
                    parse_mode="Markdown"
                )
                logger.info(f"Pago automático detectado: {pago_id}")
            except Exception as e:
                logger.error(f"Error notificando pago {pago_id}: {e}")
                registrar_error(f"verificar_pagos_automaticos - Notificación", f"Pago ID: {pago_id} | Error: {e}")