import os
import telebot
import requests
from google.generativeai import client as genai
from dotenv import load_dotenv

load_dotenv()

# === CONFIGURATION ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# === Initialiser Gemini ===
genai.configure(api_key=GEMINI_API_KEY)

# === Fonctions d’appel aux APIs ===

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
        return f"OpenRouter erreur: {e}"

def ask_gemini(prompt):
    try:
        response = genai.chat.create(
            model="models/chat-bison-001",
            messages=[{"author": "user", "content": prompt}]
        )
        return response.last
    except Exception as e:
        return f"Gemini erreur: {e}"

def ask_huggingface(prompt):
    url = "https://api-inference.huggingface.co/models/gpt2"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": prompt}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res_json = response.json()
        if isinstance(res_json, list) and len(res_json) > 0:
            return res_json[0].get('generated_text', 'Pas de réponse HuggingFace')
        else:
            return "Réponse HuggingFace inattendue"
    except Exception as e:
        return f"HuggingFace erreur: {e}"

# === Gestion des messages Telegram ===

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user = message.from_user.username or ""
    prompt = message.text

    # Exemple de logique : Ahmed reçoit la réponse Gemini, les autres OpenRouter
    if user.lower() == "ahmeds78130":
        response = ask_gemini(prompt)
    else:
        response = ask_openrouter(prompt)

    bot.reply_to(message, response)

# === Lancer le bot ===

print("PulseAIbot avec Gemini + HuggingFace + OpenRouter est en ligne...")
bot.polling()
