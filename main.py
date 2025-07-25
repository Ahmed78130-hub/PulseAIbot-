import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive  # Assure-toi d'avoir keep_alive.py dans le repo

logging.basicConfig(level=logging.INFO)

# === TES TOKENS ===
TELEGRAM_TOKEN = "8241140818:AAG7E-f1rdOyidPqVCw6e9Ma02vYYREEXRo"
GEMINI_API_KEY = "AIzaSyCbk7uzwjIUxKEQ9YtnPEFAr4ohxHfZTHc"
OPENROUTER_API_KEY = "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"

ADMIN_USERNAME = "ahmeds78130"  # sans le @

# === Fonctions pour appeler Gemini et OpenRouter ===

def ask_gemini(message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "prompt": {
            "text": message
        },
        "temperature": 0.7,
        "candidate_count": 1
    }
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["text"]
    except Exception as e:
        logging.error(f"Erreur Gemini: {e}")
        return None

def ask_openrouter(message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7
    }
    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Erreur OpenRouter: {e}")
        return None

# === Commandes Telegram ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username == ADMIN_USERNAME:
        await update.message.reply_text(f"Salam chef Ahmed 👑, PulseAIbot est prêt à t'obéir !")
    else:
        await update.message.reply_text("Salam, je suis PulseAIbot créé par Ahmed Signate.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pose moi une question, je te répondrai avec intelligence.")

# === Gestion des messages ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message.text

    if user.username == ADMIN_USERNAME:
        await update.message.reply_text("Je réfléchis... 🧠")
        # Essaie Gemini en premier
        response = ask_gemini(message)
        if not response:
            # fallback OpenRouter
            response = ask_openrouter(message)
        if not response:
            response = "Désolé, je n'ai pas pu obtenir de réponse pour le moment."
        await update.message.reply_text(response)
    else:
        await update.message.reply_text(
            "Je suis un bot créé par Ahmed Signate. Contacte @ahmeds78130 pour plus d'infos."
        )

if __name__ == '__main__':
    keep_alive()  # démarre le serveur web pour garder le bot éveillé (sur Render ou Replit)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("PulseAIbot est en ligne 🚀")
    app.run_polling()
