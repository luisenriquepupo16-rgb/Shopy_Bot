from telegram.ext import Application, CommandHandler
from config import TOKEN

async def start(update, context):
    await update.message.reply_text("✅ Bot funcionando correctamente. Comando /start recibido.")

async def precio(update, context):
    await update.message.reply_text("📋 Precios: Scripts desde 8 USDT")

def main():
    print("🤖 Iniciando bot simple...")
    print(f"📡 Token configurado: {TOKEN[:15]}... (oculto)")
    
    # Crear la aplicación
    app = Application.builder().token(TOKEN).build()
    
    # Registrar comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("precio", precio))
    
    print("✅ Handlers registrados")
    print("🔄 Iniciando polling (escuchando mensajes)...")
    print("💡 Envía /start o /precio a tu bot en Telegram")
    print("-" * 40)
    
    # Iniciar polling SIN argumentos extras (versión simple)
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("Presiona Enter para salir...")