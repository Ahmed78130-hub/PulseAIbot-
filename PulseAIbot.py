import os
from flask import Flask, request
import requests

app = Flask(__name__)

# === CONFIGURATION (via variables d'environnement) ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
AUTHORIZED_USER = "@ahmeds78130"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# === ROUTE TELEGRAM ===
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        username = "@" + data["message"]["from"].get("username", "")
        message = data["message"].get("text", "")

        if username == AUTHORIZED_USER:
            reply = get_combined_response(message)
        else:
            reply = "Bonjour 👋 Je suis PulseAIbot. Pose-moi une question !"

        send_message(chat_id, reply)
    return "OK", 200

# === ENVOYER UN MESSAGE TELEGRAM ===
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# === GEMINI ===
def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, json=payload)
    try:
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Erreur Gemini."

# === OPENROUTER ===
def ask_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    r = requests.post(url, headers=headers, json=payload)
    try:
        return r.json()['choices'][0]['message']['content']
    except:
        return "Erreur OpenRouter."

# === COMBINER LES DEUX ===
def get_combined_response(prompt):
    r1 = ask_gemini(prompt)
    r2 = ask_openrouter(prompt)
    return f"🤖 Gemini :\n{r1}\n\n🧠 OpenRouter :\n{r2}"

# === FLASK ===
@app.route("/")
def home():
    return "PulseAIbot is alive!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
