# handlers.py
# ============================================================
# MANEJADORES DE COMANDOS DEL BOT
# ============================================================

import time
import os
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS,
    WALLET_DIRECCION, MENSAJE_PAGO, MI_USER_ID
)
from database import (
    cargar_db, guardar_pago, obtener_pago, actualizar_estado_pago,
    limite_compras_por_usuario  # <-- AGREGADO: importar la nueva función
)

# ============================================================
# COMANDOS PÚBLICOS (cualquiera puede usarlos)
# ============================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de bienvenida - /start"""
    await update.message.reply_text(
        "🤖 *Bot de Venta de Scripts*\n\n"
        "Este bot vende scripts de automatización por línea de comandos.\n\n"
        "📌 *Comandos disponibles:*\n"
        "/precio - Ver scripts y precios\n"
        "/comprar [ID] - Comprar un script\n"
        "/estado [ID_pago] - Verificar estado de un pago\n\n"
        "⚠️ *No hay atención al cliente.* Este bot es completamente automático.\n\n"
        "Desarrollado con 🖤 para la comunidad",
        parse_mode="Markdown"
    )

async def cmd_precio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la lista de scripts disponibles - /precio"""
    mensaje = "📋 *Scripts disponibles:*\n\n"
    
    for script_id, nombre in NOMBRES_SCRIPTS.items():
        precio = PRECIOS.get(script_id, "?")
        desc = DESCRIPCIONES_SCRIPTS.get(script_id, "Sin descripción")
        mensaje += f"*ID: {script_id}* - {nombre}\n"
        mensaje += f"   └ {desc}\n"
        mensaje += f"   └ 💰 Precio: {precio} USDT (TRC-20)\n\n"
    
    mensaje += "Para comprar: `/comprar [ID]`\n"
    mensaje += "Ejemplo: `/comprar 1`"
    
    await update.message.reply_text(mensaje, parse_mode="Markdown")

async def cmd_comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el proceso de compra - /comprar [ID]"""
    user_id = update.effective_user.id
    args = context.args
    
    # Verificar que se haya especificado un ID
    if not args:
        await update.message.reply_text(
            "❌ *Error:* Especifica el ID del script.\n\n"
            "Uso: `/comprar [ID]`\n"
            "Ejemplo: `/comprar 1`\n\n"
            "Usa /precio para ver los IDs disponibles.",
            parse_mode="Markdown"
        )
        return
    
    script_id = args[0]
    
    # Verificar que el script existe
    if script_id not in PRECIOS:
        await update.message.reply_text(
            f"❌ *Error:* El ID '{script_id}' no es válido.\n\n"
            "Usa /precio para ver los scripts disponibles.",
            parse_mode="Markdown"
        )
        return
    
    # ============================================================
    # NUEVO BLOQUE: VERIFICAR LÍMITE DE COMPRAS POR USUARIO
    # ============================================================
    if not limite_compras_por_usuario(user_id, limite=5):
        await update.message.reply_text(
            "❌ *Límite alcanzado*\n\n"
            "Has superado el límite de 5 compras en las últimas 24 horas.\n"
            "Por favor, espera antes de realizar nuevas compras.\n\n"
            "Este límite es para proteger el sistema contra abusos.",
            parse_mode="Markdown"
        )
        return
    
    # Generar ID de pago único
    pago_id = f"{user_id}_{int(time.time())}"
    monto = PRECIOS[script_id]
    
    # Guardar el pago en la base de datos
    datos_pago = {
        "user_id": user_id,
        "script_id": script_id,
        "monto": monto,
        "estado": "pendiente",
        "fecha": time.time()
    }
    
    if guardar_pago(pago_id, datos_pago):
        mensaje_pago = MENSAJE_PAGO.format(
            direccion=WALLET_DIRECCION,
            pago_id=pago_id
        )
        
        await update.message.reply_text(
            f"💰 *Solicitud de compra generada*\n\n"
            f"📦 Script: {NOMBRES_SCRIPTS[script_id]}\n"
            f"💵 Monto: {monto} USDT (TRC-20)\n"
            f"🆔 *ID de pago:* `{pago_id}`\n\n"
            f"{mensaje_pago}\n\n"
            f"Después de pagar, usa `/estado {pago_id}` para verificar.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ *Error interno:* No se pudo generar la solicitud.\n"
            "Intenta de nuevo más tarde.",
            parse_mode="Markdown"
        )

async def cmd_estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta el estado de un pago - /estado [ID_pago]"""
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ *Error:* Especifica el ID de pago.\n\n"
            "Uso: `/estado [ID_pago]`\n"
            "Ejemplo: `/estado 123456789_1732123456`",
            parse_mode="Markdown"
        )
        return
    
    pago_id = args[0]
    pago = obtener_pago(pago_id)
    
    if not pago:
        await update.message.reply_text(
            f"❌ *Error:* No se encontró ningún pago con ID `{pago_id}`.\n\n"
            "Verifica el ID e intenta de nuevo.",
            parse_mode="Markdown"
        )
        return
    
    estado = pago["estado"]
    script_id = pago["script_id"]
    monto = pago["monto"]
    
    if estado == "pendiente":
        mensaje = (
            f"⏳ *Estado: Pendiente*\n\n"
            f"📦 Script: {NOMBRES_SCRIPTS.get(script_id, 'Desconocido')}\n"
            f"💵 Monto: {monto} USDT\n\n"
            f"Aún no se ha confirmado el pago. Una vez que envíes el pago a la dirección indicada, "
            f"el estado cambiará automáticamente cuando sea verificado manualmente."
        )
    elif estado == "pagado":
        mensaje = (
            f"✅ *Estado: Pagado (esperando entrega)*\n\n"
            f"📦 Script: {NOMBRES_SCRIPTS.get(script_id, 'Desconocido')}\n\n"
            f"El pago ha sido confirmado. En breve recibirás el enlace de descarga del script."
        )
    elif estado == "entregado":
        mensaje = (
            f"🎉 *Estado: Entregado*\n\n"
            f"📦 Script: {NOMBRES_SCRIPTS.get(script_id, 'Desconocido')}\n\n"
            f"El script ya fue enviado a este chat. Revisa tus mensajes anteriores."
        )
    else:
        mensaje = f"📌 *Estado:* {estado}"
    
    await update.message.reply_text(mensaje, parse_mode="Markdown")

# ============================================================
# COMANDOS DE ADMINISTRADOR (SOLO TÚ PUEDES USARLOS)
# ============================================================

async def cmd_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirma un pago y envía el script - SOLO ADMIN"""
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        await update.message.reply_text(
            "❌ *No autorizado.*\n\n"
            "Este comando solo puede ser usado por el administrador del bot.",
            parse_mode="Markdown"
        )
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "📌 *Uso:* `/confirmar [ID_pago]`\n\n"
            "Ejemplo: `/confirmar 123456789_1732123456`\n\n"
            "Los compradores reciben este ID cuando inician una compra.",
            parse_mode="Markdown"
        )
        return
    
    pago_id = args[0]
    pago = obtener_pago(pago_id)
    
    if not pago:
        await update.message.reply_text(
            f"❌ *Error:* No se encontró el pago con ID `{pago_id}`.",
            parse_mode="Markdown"
        )
        return
    
    if pago["estado"] != "pendiente":
        estado_actual = pago["estado"]
        await update.message.reply_text(
            f"⚠️ *Este pago ya fue procesado*\n\n"
            f"Estado actual: {estado_actual}\n"
            f"ID: `{pago_id}`",
            parse_mode="Markdown"
        )
        return
    
    script_id = pago["script_id"]
    comprador_id = pago["user_id"]
    
    script_path = f"scripts/script_{script_id}.zip"
    
    if not os.path.exists(script_path):
        await update.message.reply_text(
            f"❌ *Error:* No se encuentra el archivo del script.\n\n"
            f"Buscado en: `{script_path}`\n\n"
            "Asegúrate de tener el archivo .zip en la carpeta `scripts/`",
            parse_mode="Markdown"
        )
        return
    
    try:
        with open(script_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=comprador_id,
                document=f,
                filename=f"script_{script_id}.zip",
                caption=(
                    f"🎉 *¡Gracias por tu compra!*\n\n"
                    f"📦 Script: {NOMBRES_SCRIPTS.get(script_id, 'Desconocido')}\n\n"
                    f"📖 *Instrucciones de uso:*\n"
                    f"1. Descomprime el archivo\n"
                    f"2. Ejecuta `python main.py` o sigue las instrucciones en el README\n"
                    f"3. Consulta el archivo `ayuda.txt` si tienes dudas\n\n"
                    f"⚠️ *No hay soporte incluido.* Este script se vende 'tal cual'.\n\n"
                    f"¡Gracias por confiar en este bot! 🚀"
                ),
                parse_mode="Markdown"
            )
        
        if actualizar_estado_pago(pago_id, "entregado"):
            await update.message.reply_text(
                f"✅ *Script enviado correctamente*\n\n"
                f"📦 Script ID: {script_id}\n"
                f"👤 Comprador ID: {comprador_id}\n"
                f"🆔 Pago ID: {pago_id}\n\n"
                f"El comprador ya recibió el archivo."
            )
        else:
            await update.message.reply_text(
                f"⚠️ *Script enviado pero no se pudo actualizar la base de datos.*\n"
                f"Revisa manualmente el estado del pago {pago_id}."
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Error al enviar el script:*\n"
            f"`{str(e)}`\n\n"
            f"Verifica que el comprador {comprador_id} no haya bloqueado al bot.\n"
            f"El bot no puede enviar mensajes si el usuario no inició una conversación con `/start`.",
            parse_mode="Markdown"
        )

async def cmd_listar_pagos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista todos los pagos pendientes - SOLO ADMIN"""
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        await update.message.reply_text("❌ No autorizado.")
        return
    
    db = cargar_db()
    pagos_pendientes = db.get("pagos_pendientes", {})
    
    if not pagos_pendientes:
        await update.message.reply_text("📭 No hay pagos pendientes.")
        return
    
    mensaje = "📋 *Pagos pendientes:*\n\n"
    for pago_id, datos in pagos_pendientes.items():
        if datos["estado"] == "pendiente":
            mensaje += f"🆔 `{pago_id}`\n"
            mensaje += f"   └ Script: {datos['script_id']} | Monto: {datos['monto']} USDT\n"
            mensaje += f"   └ Usuario: {datos['user_id']}\n\n"
    
    mensaje += "Para confirmar uno: `/confirmar [ID_pago]`"
    await update.message.reply_text(mensaje, parse_mode="Markdown")