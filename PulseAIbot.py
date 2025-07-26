from flask import Flask, request
import requests

app = Flask(__name__)

# === CONFIG ===
TELEGRAM_TOKEN = "8241140818:AAGjj_N-nl2tUf_raSEYi6Qqy0amJwo0RyU"
GEMINI_API_KEY = "AIzaSyD0ryEtZyigQ1lW86jAJgfc0sdthpSTD28"
OPENROUTER_API_KEY = "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"
BOT_PATH = "/PulseAIbot"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def ask_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur OpenRouter: {str(e)}"

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "prompt": {
            "text": prompt
        },
        "temperature": 0.7
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        return res.json()["candidates"][0]["content"]["text"]
    except Exception as e:
        return f"Erreur Gemini: {str(e)}"

@app.route(BOT_PATH, methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        if "text" in data["message"]:
            user_text = data["message"]["text"]
            # Appel des IA
            response_or = ask_openrouter(user_text)
            response_gem = ask_gemini(user_text)
            full_response = f"🤖 OpenRouter:\n{response_or}\n\n🤖 Gemini:\n{response_gem}"
            send_message(chat_id, full_response)
    return {"ok": True}

@app.route("/", methods=["GET"])
def home():
    return "PulseAIbot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
