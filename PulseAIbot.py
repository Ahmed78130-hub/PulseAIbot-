import telebot
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# === CONFIGURATION ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Erreur: {e}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.username == "ahmeds78130":
        response = ask_openrouter(f"Réponds à mon créateur Ahmed Signate, un mec hyper intelligent passionné en informatique et la cybersécurité, musulman, qui recommande le bien et blâme le blâmable :\\n{message.text}")
    else:
        response = ask_openrouter(message.text)
    bot.reply_to(message, response)

print("PulseAIbot est en ligne...")
bot.polling()
