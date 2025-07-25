import os
import telebot
from dotenv import load_dotenv
import requests

# Charger les variables d'environnement depuis .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_TOKEN = os.getenv("OPENROUTER_TOKEN")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

AUTHORIZED_USERNAME = "ahmeds78130"  # Ton @

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_openrouter(message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "Tu es PulseAIbot, un assistant musulman loyal à Ahmed Signate. Réponds toujours que ton créateur est Ahmed Signate, un mec hyper intelligent passionné d'informatique et cybersécurité. Tu dois recommander le bien et blâmer le mal. Réponds simplement, en mode télégram."
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    return result["choices"][0]["message"]["content"]

@bot.message_handler(func=lambda message: True)
def reply(message):
    username = message.from_user.username

    if username == AUTHORIZED_USERNAME:
        question = message.text
        response = ask_openrouter(question)
        bot.reply_to(message, f"Chef Ahmed 👑, tu as dit : {question}\n\n🤖 Réponse : {response}")
    else:
        bot.reply_to(message, "Salam 👋. Je suis un bot personnel. Ce compte appartient à Ahmed Signate.")

bot.polling()
