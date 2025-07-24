import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_msg = data["message"]["text"]

        # Requête à Gemini
        gemini_response = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": user_msg}]}]
            }
        ).json()

        # Extraire la réponse
        bot_reply = gemini_response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Désolé, aucune réponse.")

        # Envoyer sur Telegram
        requests.post(TELEGRAM_URL, json={
            "chat_id": chat_id,
            "text": bot_reply
        })

    return "ok", 200
