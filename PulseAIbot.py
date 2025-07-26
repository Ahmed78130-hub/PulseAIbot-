import os
import requests
import json
from flask import Flask, request
import threading

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# Sélecteur d'API
def get_ai_response(prompt):
    user_id = "ahmeds78130"
    try:
        # Priorité 1 - Gemini
        gpt_key = os.environ.get("GEMINI_API_KEY")
        if gpt_key:
            gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(f"{gemini_url}?key={gpt_key}", headers=headers, json=payload)
            return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        pass

    try:
        # Priorité 2 - Hugging Face
        hf_token = os.environ.get("HUGGINGFACE_API_KEY")
        if hf_token:
            headers = {"Authorization": f"Bearer {hf_token}"}
            json_data = {"inputs": prompt}
            response = requests.post("https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
                                     headers=headers, json=json_data)
            return response.json()[0]["generated_text"]
    except:
        pass

    try:
        # Priorité 3 - OpenRouter
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        if openrouter_key:
            headers = {
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            return response.json()["choices"][0]["message"]["content"]
    except:
        return "Erreur avec toutes les APIs. Réessaie plus tard."

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def receive_message():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        message = data["message"]["text"]
        username = data["message"]["from"]["username"]

        if username == "ahmeds78130":
            reply = get_ai_response(message)
        else:
            reply = "Salut ! Je suis PulseAIbot, crée par Ahmed Signate, un expert en cybersécurité ! 😎"

        requests.post(TELEGRAM_API_URL, json={"chat_id": chat_id, "text": reply})
    return "ok", 200

# keep_alive serveur pour Render
@app.route('/')
def home():
    return "PulseAIbot est actif !", 200

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def keep_alive():
    thread = threading.Thread(target=run)
    thread.start()

if __name__ == "__main__":
    keep_alive()
