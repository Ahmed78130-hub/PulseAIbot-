import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Tokens dans variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(question):
    url = "https://generativelanguage.googleapis.com/v1beta2/models/chat-bison-001:generateMessage"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}",
    }
    data = {
        "prompt": {
            "messages": [
                {"author": "user", "content": question}
            ]
        },
        "temperature": 0.2,
        "candidateCount": 1
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        res_json = response.json()
        try:
            return res_json["candidates"][0]["content"]
        except (KeyError, IndexError):
            return "Désolé, je n'ai pas pu comprendre la réponse."
    else:
        return "Erreur lors de la requête à Gemini."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut ! Je suis ton bot, prêt à discuter.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    réponse = ask_gemini(question)
    await update.message.reply_text(réponse)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot lancé...")
    app.run_polling()
