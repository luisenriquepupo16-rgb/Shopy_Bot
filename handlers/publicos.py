# handlers/publicos.py
import time
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    PRECIOS, NOMBRES_SCRIPTS, DESCRIPCIONES_SCRIPTS,
    WALLET_DIRECCION, MENSAJE_PAGO
)
from database import (
    guardar_pago, obtener_pago,
    limite_compras_por_usuario,
    obtener_idioma_usuario, guardar_idioma_usuario,
    registrar_error
)
from .textos import get_text
from .comunes import generar_monto_unico

logger = logging.getLogger(__name__)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = get_text(user_id, "start")
    await update.message.reply_text(text, parse_mode=None)
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
    await update.message.reply_text(mensaje, parse_mode=None)
    logger.info(f"Usuario {user_id} ejecutó /price")

async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    
    logger.info(f"Usuario {user_id} ejecutó /buy con args: {args}")
    
    if not args:
        text = get_text(user_id, "buy_error_no_id")
        await update.message.reply_text(text, parse_mode=None)
        return
    
    script_id = args[0]
    logger.info(f"Usuario {user_id} - Script ID solicitado: {script_id}")
    
    if script_id not in PRECIOS:
        text = get_text(user_id, "buy_error_invalid_id", script_id=script_id)
        await update.message.reply_text(text, parse_mode=None)
        return
    
    try:
        if not limite_compras_por_usuario(user_id, limite=5):
            text = get_text(user_id, "buy_limit_reached")
            await update.message.reply_text(text, parse_mode=None)
            return
    except Exception as e:
        logger.error(f"Error al verificar límite para {user_id}: {e}")
        registrar_error(f"cmd_buy - Límite de compras", f"Usuario {user_id} | Error: {e}")
        text = get_text(user_id, "buy_internal_error")
        await update.message.reply_text(text, parse_mode=None)
        return
    
    pago_id = f"{user_id}_{int(time.time())}"
    precio_base = PRECIOS[script_id]
    monto_final = generar_monto_unico(precio_base)
    logger.info(f"Usuario {user_id} - Precio base: {precio_base}, Monto final: {monto_final}")
    
    datos_pago = {
        "user_id": user_id,
        "script_id": script_id,
        "monto": monto_final,
        "precio_base": precio_base,
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
                                monto=monto_final,
                                pago_id=pago_id,
                                mensaje_pago=mensaje_pago)
            
            await update.message.reply_text(respuesta, parse_mode=None)
            logger.info(f"Usuario {user_id} - Respuesta de compra enviada correctamente")
        else:
            logger.error(f"Usuario {user_id} - Error al guardar pago en DB")
            registrar_error(f"cmd_buy - Guardar pago", f"Usuario {user_id} | Script {script_id}")
            text = get_text(user_id, "buy_db_error")
            await update.message.reply_text(text, parse_mode=None)
    
    except Exception as e:
        logger.error(f"Usuario {user_id} - Excepción en cmd_buy: {e}")
        registrar_error(f"cmd_buy - Excepción", f"Usuario {user_id} | Error: {e}")
        text = get_text(user_id, "buy_technical_error", error=str(e)[:100])
        await update.message.reply_text(text, parse_mode=None)

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        text = get_text(user_id, "status_error_no_id")
        await update.message.reply_text(text, parse_mode=None)
        return
    
    pago_id = args[0]
    pago = obtener_pago(pago_id)
    
    if not pago:
        text = get_text(user_id, "status_error_not_found", pago_id=pago_id)
        await update.message.reply_text(text, parse_mode=None)
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
    
    await update.message.reply_text(text, parse_mode=None)

async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_actual = obtener_idioma_usuario(user_id)
    
    if lang_actual == "en":
        guardar_idioma_usuario(user_id, "es")
        text = "✅ Idioma cambiado a Español.\n\nUsa /language para volver a Inglés."
    else:
        guardar_idioma_usuario(user_id, "en")
        text = "✅ Language changed to English.\n\nUse /language to switch to Spanish."
    
    await update.message.reply_text(text, parse_mode=None)
    logger.info(f"Usuario {user_id} cambió idioma a {'es' if lang_actual == 'en' else 'en'}")