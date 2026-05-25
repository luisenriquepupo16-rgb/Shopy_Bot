# handlers/periodic.py
import logging
from telegram.ext import ContextTypes

from config import WALLET_DIRECCION, MI_USER_ID
from database import (
    cargar_db, actualizar_estado_pago, verificar_pago_usdt_trc20,
    registrar_error
)
from .textos import TEXTOS

logger = logging.getLogger(__name__)

async def verificar_pagos_automaticos(context: ContextTypes.DEFAULT_TYPE):
    db = cargar_db()
    
    for pago_id, datos in db["pagos_pendientes"].items():
        if datos["estado"] != "pendiente":
            continue
        
        monto_esperado = datos["monto"]
        precio_base = datos.get("precio_base", monto_esperado)
        
        pago = verificar_pago_usdt_trc20(WALLET_DIRECCION, monto_esperado, timeout_minutos=60)
        
        if not pago and precio_base != monto_esperado:
            logger.info(f"Buscando pago con precio base {precio_base} para {pago_id}")
            pago = verificar_pago_usdt_trc20(WALLET_DIRECCION, precio_base, timeout_minutos=60)
        
        if pago:
            actualizar_estado_pago(pago_id, "pagado")
            
            text = TEXTOS["en"]["payment_detected"].format(
                pago_id=pago_id,
                monto=pago["monto"],
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