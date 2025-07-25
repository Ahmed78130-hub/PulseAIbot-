import os
import requests
from flask import Flask, request
from google.generativeai import GenerativeModel, configure

# === CONFIGURATION ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

configure(api_key=GEMINI_API_KEY)
model = GenerativeModel("gemini-pro")

app = Flask(__name__)

# === FONCTION POUR ENVOYER UN MESSAGE TELEGRAM ===
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# === ROUTE WEBHOOK ===
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Message reçu :", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        # Interroge Gemini
        try:
            response = model.generate_content(user_message)
            reply = response.text
        except Exception as e:
            reply = f"Erreur Gemini : {str(e)}"

        send_telegram_message(chat_id, reply)

    return {"ok": True}

# === TEST DE VIE ===
@app.route("/", methods=["GET"])
def index():
    return "Bot Gemini Telegram actif !"

if __name__ == "__main__":
    app.run(debug=True)
