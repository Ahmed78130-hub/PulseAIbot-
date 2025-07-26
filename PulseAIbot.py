from flask import Flask, request
import requests
import google.generativeai as genai
import os

# ======== CONFIGURATION ========
TELEGRAM_TOKEN = "TON_TOKEN_TELEGRAM"
OPENROUTER_API_KEY = "sk-...openrouter"
GEMINI_API_KEY = "AIzaSy..."  # Gemini
HUGGINGFACE_API_KEY = "hf_..."  # Hugging Face

# ==== CONFIGURATION Gemini ====
genai.configure(api_key=GEMINI_API_KEY)

# ==== DÉMARRAGE DU BOT ====
app = Flask(__name__)

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat()
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"Gemini erreur: {e}"

def ask_huggingface(prompt):
    try:
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {"inputs": prompt}
        response = requests.post(
            "https://api-inference.huggingface.co/models/bigscience/bloom",
            headers=headers, json=payload)
        result = response.json()
        return result[0]["generated_text"] if isinstance(result, list) else str(result)
    except Exception as e:
        return f"HuggingFace erreur: {e}"

def ask_openrouter(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        json_data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=json_data)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"OpenRouter erreur: {e}"

def generate_response(prompt):
    # Tu peux choisir quelle IA tu veux prioriser ou combiner
    gemini_reply = ask_gemini(prompt)
    hf_reply = ask_huggingface(prompt)
    or_reply = ask_openrouter(prompt)
    return f"🧠 Gemini:\n{gemini_reply}\n\n🤖 HuggingFace:\n{hf_reply}\n\n🌍 OpenRouter:\n{or_reply}"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        prompt = data["message"]["text"]
        reply = generate_response(prompt)
        send_telegram(chat_id, reply)
    return "OK"

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text[:4096]})

@app.route("/")
def home():
    return "Bot en ligne 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
