import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === CONFIGURATION ===
TELEGRAM_TOKEN = "8241140818:AAG7E-f1rdOyidPqVCw6e9Ma02vYYREEXRo"

# === LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === COMMANDES ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username == "ahmeds78130":
        await update.message.reply_text("Bienvenue chef Ahmed ! Ton bot est prêt à te servir ! 🔥")
    else:
        await update.message.reply_text("Salam 👋 Je suis PulseAIbot, assistant personnel basé sur l’IA.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Utilise /start pour commencer. Pose-moi une question ensuite.")

# === RÉPONSE GÉNÉRALE ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message.text.lower()

    if user.username == "ahmeds78130":
        response = f"Chef Ahmed 👑, tu as dit : {message}"
    else:
        response = "Je suis PulseAIbot, créé par Ahmed Signate, un mec hyper intelligent passionné en cybersécurité et croyant en Allah."

    await update.message.reply_text(response)

# === MAIN ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
