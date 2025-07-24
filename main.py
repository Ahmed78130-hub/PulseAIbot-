import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import google.generativeai as genai
from transformers import pipeline

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

# Config Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-pro")

# Setup Hugging Face pipeline pour traduction en français
translator = pipeline("translation_en_to_fr", model="Helsinki-NLP/opus-mt-en-fr", token=HF_API_KEY)

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bienvenue ! Je suis PulseAIbot 🤖 avec Gemini & Hugging Face 🔥")

# Gestion des messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "qui" in text and ("créé" in text or "createur" in text):
        await update.message.reply_text(
            "Mon créateur, c’est Ahmed. Le seul, l’unique, le génie. 💯"
        )
    elif text.startswith("traduis:"):
        phrase = text.replace("traduis:", "").strip()
        result = translator(phrase)
        await update.message.reply_text(f"🇫🇷 Traduction : {result[0]['translation_text']}")
    else:
        response = gemini_model.generate_content(text)
        await update.message.reply_text(response.text)

# Lancer le bot
if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("❌ Le token Telegram est manquant.")
    else:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        logger.info("🚀 PulseAIbot lancé.")
        app.run_polling()
