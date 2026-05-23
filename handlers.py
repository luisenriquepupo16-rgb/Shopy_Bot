# handlers.py
# ============================================================
# MANEJADORES DE COMANDOS DEL BOT - VERSION 1.3
# ============================================================

import time
import os
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS,
    WALLET_DIRECCION, MENSAJE_PAGO, MI_USER_ID
)
from database import (
    cargar_db, guardar_pago, obtener_pago, actualizar_estado_pago,
    limite_compras_por_usuario
)

logger = logging.getLogger(__name__)

# ============================================================
# COMANDOS PÚBLICOS
# ============================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "🤖 Bot de Venta de Scripts\n\n"
        "Este bot vende scripts de automatización por línea de comandos.\n\n"
        "Comandos disponibles:\n"
        "/precio - Ver scripts y precios\n"
        "/comprar [ID] - Comprar un script\n"
        "/estado [ID_pago] - Verificar estado de un pago\n\n"
        "⚠️ No hay atención al cliente. Este bot es completamente automático."
    )
    await update.message.reply_text(mensaje)
    logger.info(f"Usuario {update.effective_user.id} ejecutó /start")

async def cmd_precio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = "📋 Scripts disponibles:\n\n"
    
    for script_id, nombre in NOMBRES_SCRIPTS.items():
        precio = PRECIOS.get(script_id, "?")
        desc = DESCRIPCIONES_SCRIPTS.get(script_id, "Sin descripción")
        mensaje += f"ID: {script_id} - {nombre}\n"
        mensaje += f"   └ {desc}\n"
        mensaje += f"   └ Precio: {precio} USDT (TRC-20)\n\n"
    
    mensaje += "Para comprar: /comprar [ID]\n"
    mensaje += "Ejemplo: /comprar 1"
    
    await update.message.reply_text(mensaje)
    logger.info(f"Usuario {update.effective_user.id} ejecutó /precio")

async def cmd_comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    
    logger.info(f"Usuario {user_id} ejecutó /comprar con args: {args}")
    
    # Verificar argumentos
    if not args:
        logger.warning(f"Usuario {user_id} - No especificó ID")
        await update.message.reply_text(
            "❌ Error: Especifica el ID del script.\n\n"
            "Uso: /comprar [ID]\n"
            "Ejemplo: /comprar 1\n\n"
            "Usa /precio para ver los IDs disponibles."
        )
        return
    
    script_id = args[0]
    logger.info(f"Usuario {user_id} - Script ID solicitado: {script_id}")
    
    # Verificar existencia
    if script_id not in PRECIOS:
        logger.warning(f"Usuario {user_id} - Script ID {script_id} no existe")
        await update.message.reply_text(
            f"❌ Error: El ID '{script_id}' no es válido.\n\n"
            "Usa /precio para ver los scripts disponibles."
        )
        return
    
    # Verificar límite
    try:
        if not limite_compras_por_usuario(user_id, limite=5):
            logger.warning(f"Usuario {user_id} - Límite de compras alcanzado")
            await update.message.reply_text(
                "❌ Límite alcanzado\n\n"
                "Has superado el límite de 5 compras en las últimas 24 horas.\n"
                "Por favor, espera antes de realizar nuevas compras."
            )
            return
    except Exception as e:
        logger.error(f"Error al verificar límite para {user_id}: {e}")
        await update.message.reply_text("Error interno. Intenta de nuevo más tarde.")
        return
    
    # Generar pago
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
            
            respuesta = (
                f"💰 Solicitud de compra generada\n\n"
                f"📦 Script: {NOMBRES_SCRIPTS[script_id]}\n"
                f"💵 Monto: {monto} USDT (TRC-20)\n"
                f"🆔 ID de pago: {pago_id}\n\n"
                f"{mensaje_pago}\n\n"
                f"Después de pagar, usa /estado {pago_id} para verificar."
            )
            
            await update.message.reply_text(respuesta)
            logger.info(f"Usuario {user_id} - Respuesta de compra enviada correctamente")
        else:
            logger.error(f"Usuario {user_id} - Error al guardar pago en DB")
            await update.message.reply_text("❌ Error interno: No se pudo generar la solicitud. Intenta de nuevo más tarde.")
    
    except Exception as e:
        logger.error(f"Usuario {user_id} - Excepción en cmd_comprar: {e}")
        await update.message.reply_text(f"❌ Error técnico: {str(e)[:100]}")

async def cmd_estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ Error: Especifica el ID de pago.\n\n"
            "Uso: /estado [ID_pago]\n"
            "Ejemplo: /estado 123456789_1732123456"
        )
        return
    
    pago_id = args[0]
    pago = obtener_pago(pago_id)
    
    if not pago:
        await update.message.reply_text(
            f"❌ Error: No se encontró ningún pago con ID {pago_id}.\n\n"
            "Verifica el ID e intenta de nuevo."
        )
        return
    
    estado = pago["estado"]
    script_id = pago["script_id"]
    monto = pago["monto"]
    
    if estado == "pendiente":
        mensaje = (
            f"⏳ Estado: Pendiente\n\n"
            f"📦 Script: {NOMBRES_SCRIPTS.get(script_id, 'Desconocido')}\n"
            f"💵 Monto: {monto} USDT\n\n"
            f"Aún no se ha confirmado el pago."
        )
    elif estado == "pagado":
        mensaje = (
            f"✅ Estado: Pagado (esperando entrega)\n\n"
            f"📦 Script: {NOMBRES_SCRIPTS.get(script_id, 'Desconocido')}\n\n"
            f"El pago ha sido confirmado. En breve recibirás el script."
        )
    elif estado == "entregado":
        mensaje = (
            f"🎉 Estado: Entregado\n\n"
            f"📦 Script: {NOMBRES_SCRIPTS.get(script_id, 'Desconocido')}\n\n"
            f"El script ya fue enviado a este chat."
        )
    else:
        mensaje = f"📌 Estado: {estado}"
    
    await update.message.reply_text(mensaje)

# ============================================================
# COMANDOS DE ADMINISTRADOR
# ============================================================

async def cmd_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        await update.message.reply_text("❌ No autorizado.")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "📌 Uso: /confirmar [ID_pago]\n\n"
            "Ejemplo: /confirmar 123456789_1732123456"
        )
        return
    
    pago_id = args[0]
    pago = obtener_pago(pago_id)
    
    if not pago:
        await update.message.reply_text(f"❌ Error: No se encontró el pago {pago_id}")
        return
    
    if pago["estado"] != "pendiente":
        await update.message.reply_text(f"⚠️ Este pago ya fue procesado. Estado: {pago['estado']}")
        return
    
    script_id = pago["script_id"]
    comprador_id = pago["user_id"]
    script_path = f"scripts/script_{script_id}.zip"
    
    if not os.path.exists(script_path):
        await update.message.reply_text(f"❌ Error: No se encuentra el archivo {script_path}")
        return
    
    try:
        with open(script_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=comprador_id,
                document=f,
                filename=f"script_{script_id}.zip",
                caption=f"🎉 Gracias por tu compra!\n\nScript: {NOMBRES_SCRIPTS.get(script_id, 'Desconocido')}\n\nNo hay soporte incluido."
            )
        
        if actualizar_estado_pago(pago_id, "entregado"):
            await update.message.reply_text(f"✅ Script enviado correctamente a {comprador_id}")
        else:
            await update.message.reply_text(f"⚠️ Script enviado pero no se actualizó la DB")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar: {str(e)[:200]}")

async def cmd_listar_pagos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != MI_USER_ID:
        await update.message.reply_text("❌ No autorizado.")
        return
    
    db = cargar_db()
    pagos_pendientes = db.get("pagos_pendientes", {})
    
    if not pagos_pendientes:
        await update.message.reply_text("📭 No hay pagos pendientes.")
        return
    
    mensaje = "📋 Pagos pendientes:\n\n"
    for pago_id, datos in pagos_pendientes.items():
        if datos["estado"] == "pendiente":
            mensaje += f"🆔 {pago_id}\n"
            mensaje += f"   └ Script: {datos['script_id']} | Monto: {datos['monto']} USDT\n"
            mensaje += f"   └ Usuario: {datos['user_id']}\n\n"
    
    mensaje += "Para confirmar: /confirmar [ID_pago]"
    await update.message.reply_text(mensaje)

