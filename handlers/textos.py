# handlers/textos.py
from database import obtener_idioma_usuario

TEXTOS = {
    "en": {
        "start": (
            "🤖 Script Sales Bot\n\n"
            "This bot sells automation scripts for command line.\n\n"
            "Available commands:\n"
            "/price - View scripts and prices\n"
            "/buy [ID] - Buy a script\n"
            "/status [payment_ID] - Check payment status\n"
            "/language - Change language (Español/English)\n\n"
            "⚠️ No customer support. This bot is fully automated."
        ),
        "price_title": "📋 Available scripts:\n\n",
        "price_buy": "\nTo buy: /buy [ID]\nExample: /buy 1",
        "price_id": "ID: {script_id} - {nombre}\n   └ {desc}\n   └ Price: {precio} USDT (TRC-20)\n",
        "buy_error_no_id": "❌ Error: Specify script ID.\n\nUsage: /buy [ID]\nExample: /buy 1\n\nUse /price to see available IDs.",
        "buy_error_invalid_id": "❌ Error: ID '{script_id}' is not valid.\n\nUse /price to see available scripts.",
        "buy_limit_reached": "❌ Limit reached\n\nYou have exceeded the limit of 5 purchases in the last 24 hours.\nPlease wait before making new purchases.",
        "buy_internal_error": "Internal error. Please try again later.",
        "buy_success": (
            "💰 Purchase request generated\n\n"
            "📦 Script: {nombre}\n"
            "💵 Amount: {monto} USDT (TRC-20)\n"
            "🆔 Payment ID: {pago_id}\n\n"
            "{mensaje_pago}\n\n"
            "After paying, use /status {pago_id} to verify."
        ),
        "buy_db_error": "❌ Internal error: Could not generate request. Try again later.",
        "buy_technical_error": "❌ Technical error: {error}",
        "status_error_no_id": "❌ Error: Specify payment ID.\n\nUsage: /status [payment_ID]\nExample: /status 123456789_1732123456",
        "status_error_not_found": "❌ Error: No payment found with ID {pago_id}.\n\nCheck the ID and try again.",
        "status_pending": "⏳ Status: Pending\n\n📦 Script: {nombre}\n💵 Amount: {monto} USDT\n\nPayment not yet confirmed.",
        "status_paid": "✅ Status: Paid (awaiting delivery)\n\n📦 Script: {nombre}\n\nPayment confirmed. You will receive the script shortly.",
        "status_delivered": "🎉 Status: Delivered\n\n📦 Script: {nombre}\n\nThe script has been sent to this chat.",
        "status_unknown": "📌 Status: {estado}",
        "confirm_not_authorized": "❌ Not authorized.",
        "confirm_usage": "📌 Usage: /confirm [payment_ID]\n\nExample: /confirm 123456789_1732123456",
        "confirm_not_found": "❌ Error: Payment {pago_id} not found.",
        "confirm_already_processed": "⚠️ This payment was already processed. Status: {estado}",
        "confirm_file_not_found": "❌ Error: Script file not found in GitHub Release",
        "confirm_sent": "✅ Script sent successfully to {comprador_id}",
        "confirm_db_error": "⚠️ Script sent but database not updated",
        "confirm_send_error": "❌ Error sending: {error}",
        "list_not_authorized": "❌ Not authorized.",
        "list_empty": "📭 No pending payments.",
        "list_title": "📋 Pending payments:\n\n",
        "list_item": "🆔 {pago_id}\n   └ Script: {script_id} | Amount: {monto} USDT\n   └ User: {user_id}\n",
        "list_footer": "\nTo confirm: /confirm [payment_ID]",
        "language_changed": "✅ Language changed to Spanish.\n\nUse /language to switch back to English.",
        "language_changed_en": "✅ Language changed to English.\n\nUse /language to switch to Spanish.",
        "payment_detected": "✅ Payment detected automatically!\n\nID: {pago_id}\nAmount: {monto} USDT\nTx: {tx_id}...\n\nUse /confirm {pago_id} to deliver the script.",
        "errors_empty": "✅ No errors registered in the system.",
        "errors_title": "📋 Last errors registered:\n\n",
        "save_db_start": "💾 Saving database backup...",
        "save_db_success": "✅ Backup saved successfully!\n\nDatabase has been backed up to GitHub Gist.\nIt will be restored automatically on next restart.",
        "save_db_error": "❌ Error saving backup\n\nCheck that BACKUP_GIST_ID and GITHUB_TOKEN are configured.",
        # ============================================================
        # ESTADÍSTICAS (STATS)
        # ============================================================
        "stats_title": "📊 BOT STATISTICS\n\n",
        "stats_earned": "💰 Total earned: {total_ganado:.2f} USDT\n",
        "stats_purchases": "📦 Total purchases: {total_compras}\n",
        "stats_average": "⭐ Average per sale: {promedio:.2f} USDT\n\n",
        "stats_top_title": "📋 Top scripts:\n",
        "stats_top_item": "   {script_id}. {nombre}: {cantidad} sale(s)\n",
        "stats_no_sales": "   No sales recorded yet.\n",
        "stats_status": "\n🟢 Status: Active on Railway"
    },
    "es": {
        "start": (
            "🤖 Bot de Venta de Scripts\n\n"
            "Este bot vende scripts de automatización por línea de comandos.\n\n"
            "Comandos disponibles:\n"
            "/price - Ver scripts y precios\n"
            "/buy [ID] - Comprar un script\n"
            "/status [ID_pago] - Verificar estado de pago\n"
            "/language - Cambiar idioma (Español/English)\n\n"
            "⚠️ No hay atención al cliente. Este bot es completamente automático."
        ),
        "price_title": "📋 Scripts disponibles:\n\n",
        "price_buy": "\nPara comprar: /buy [ID]\nEjemplo: /buy 1",
        "price_id": "ID: {script_id} - {nombre}\n   └ {desc}\n   └ Precio: {precio} USDT (TRC-20)\n",
        "buy_error_no_id": "❌ Error: Especifica el ID del script.\n\nUso: /buy [ID]\nEjemplo: /buy 1\n\nUsa /price para ver los IDs disponibles.",
        "buy_error_invalid_id": "❌ Error: El ID '{script_id}' no es válido.\n\nUsa /price para ver los scripts disponibles.",
        "buy_limit_reached": "❌ Límite alcanzado\n\nHas superado el límite de 5 compras en las últimas 24 horas.\nPor favor, espera antes de realizar nuevas compras.",
        "buy_internal_error": "Error interno. Intenta de nuevo más tarde.",
        "buy_success": (
            "💰 Solicitud de compra generada\n\n"
            "📦 Script: {nombre}\n"
            "💵 Monto: {monto} USDT (TRC-20)\n"
            "🆔 ID de pago: {pago_id}\n\n"
            "{mensaje_pago}\n\n"
            "Después de pagar, usa /status {pago_id} para verificar."
        ),
        "buy_db_error": "❌ Error interno: No se pudo generar la solicitud. Intenta de nuevo más tarde.",
        "buy_technical_error": "❌ Error técnico: {error}",
        "status_error_no_id": "❌ Error: Especifica el ID de pago.\n\nUso: /status [ID_pago]\nEjemplo: /status 123456789_1732123456",
        "status_error_not_found": "❌ Error: No se encontró ningún pago con ID {pago_id}.\n\nVerifica el ID e intenta de nuevo.",
        "status_pending": "⏳ Estado: Pendiente\n\n📦 Script: {nombre}\n💵 Monto: {monto} USDT\n\nAún no se ha confirmado el pago.",
        "status_paid": "✅ Estado: Pagado (esperando entrega)\n\n📦 Script: {nombre}\n\nEl pago ha sido confirmado. En breve recibirás el script.",
        "status_delivered": "🎉 Estado: Entregado\n\n📦 Script: {nombre}\n\nEl script ya fue enviado a este chat.",
        "status_unknown": "📌 Estado: {estado}",
        "confirm_not_authorized": "❌ No autorizado.",
        "confirm_usage": "📌 Uso: /confirm [ID_pago]\n\nEjemplo: /confirm 123456789_1732123456",
        "confirm_not_found": "❌ Error: No se encontró el pago {pago_id}.",
        "confirm_already_processed": "⚠️ Este pago ya fue procesado. Estado: {estado}",
        "confirm_file_not_found": "❌ Error: No se encontró el archivo del script en GitHub Release",
        "confirm_sent": "✅ Script enviado correctamente a {comprador_id}",
        "confirm_db_error": "⚠️ Script enviado pero no se actualizó la base de datos",
        "confirm_send_error": "❌ Error al enviar: {error}",
        "list_not_authorized": "❌ No autorizado.",
        "list_empty": "📭 No hay pagos pendientes.",
        "list_title": "📋 Pagos pendientes:\n\n",
        "list_item": "🆔 {pago_id}\n   └ Script: {script_id} | Monto: {monto} USDT\n   └ Usuario: {user_id}\n",
        "list_footer": "\nPara confirmar: /confirm [ID_pago]",
        "language_changed": "✅ Idioma cambiado a Inglés.\n\nUsa /language para volver a Español.",
        "language_changed_en": "✅ Language changed to English.\n\nUse /language to switch to Spanish.",
        "payment_detected": "✅ ¡Pago detectado automáticamente!\n\nID: {pago_id}\nMonto: {monto} USDT\nTx: {tx_id}...\n\nUsa /confirm {pago_id} para entregar el script.",
        "errors_empty": "✅ No hay errores registrados en el sistema.",
        "errors_title": "📋 Últimos errores registrados:\n\n",
        "save_db_start": "💾 Guardando respaldo de la base de datos...",
        "save_db_success": "✅ Respaldo guardado exitosamente!\n\nLa base de datos ha sido respaldada en GitHub Gist.\nSe restaurará automáticamente al reiniciar el bot.",
        "save_db_error": "❌ Error guardando respaldo\n\nVerifica que BACKUP_GIST_ID y GITHUB_TOKEN estén configurados.",
        # ============================================================
        # ESTADÍSTICAS (STATS)
        # ============================================================
        "stats_title": "📊 ESTADÍSTICAS DEL BOT\n\n",
        "stats_earned": "💰 Total ganado: {total_ganado:.2f} USDT\n",
        "stats_purchases": "📦 Total compras: {total_compras}\n",
        "stats_average": "⭐ Promedio por venta: {promedio:.2f} USDT\n\n",
        "stats_top_title": "📋 Scripts más vendidos:\n",
        "stats_top_item": "   {script_id}. {nombre}: {cantidad} venta(s)\n",
        "stats_no_sales": "   No hay ventas registradas aún.\n",
        "stats_status": "\n🟢 Estado: Activo en Railway"
    }
}

def get_text(user_id, key, **kwargs):
    """Obtiene el texto en el idioma del usuario"""
    lang = obtener_idioma_usuario(user_id)
    text = TEXTOS.get(lang, TEXTOS["en"]).get(key, TEXTOS["en"][key])
    # Si hay kwargs, formatear; si no, devolver el texto directamente
    if kwargs:
        return text.format(**kwargs)
    return text