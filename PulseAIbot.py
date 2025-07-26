from flask import Flask, request
import requests
import google.generativeai as genai
from transformers import pipeline
import os
import logging

# ============ CONFIGURATION DES CLÉS =============
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# ============ INIT FLASK ==========================
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ============ INIT GEMINI =========================
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-pro")

# ============ INIT HUGGING FACE ===================
huggingface_pipe = pipeline("text-generation", model="gpt2", use_auth_token=HUGGINGFACE_API_KEY)

# ============ FUNCTION OPENROUTER =================
def ask_openrouter(message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openrouter/openchat",
        "messages": [{"role": "user", "content": message}]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        res.raise_for_status()
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Erreur OpenRouter : {str(e)}"

# ============ FUNCTION GEMINI =====================
def ask_gemini(message):
    try:
        convo = gemini_model.start_chat(history=[])
        response = convo.send_message(message)
        return response.text
    except Exception as e:
        return f"Erreur Gemini : {str(e)}"

# ============ FUNCTION HUGGING FACE ===============
def ask_huggingface(message):
    try:
        result = huggingface_pipe(message, max_length=100, do_sample=True)
        return result[0]["generated_text"]
    except Exception as e:
        return f"Erreur HuggingFace : {str(e)}"

# ============ TELEGRAM WEBHOOK ====================
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        # Générer une réponse combinée
        gemini_reply = ask_gemini(user_message)
        openrouter_reply = ask_openrouter(user_message)
        huggingface_reply = ask_huggingface(user_message)

        final_reply = (
            f"🤖 *Gemini* :\n{gemini_reply}\n\n"
            f"🌐 *OpenRouter* :\n{openrouter_reply}\n\n"
            f"🧠 *Hugging Face* :\n{huggingface_reply}"
        )

        # Envoyer la réponse
        send_message(chat_id, final_reply)

    return {"ok": True}

# ============ SEND MESSAGE ========================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logging.error(f"Erreur envoi message : {e}")

# ============ PING ROUTE POUR GARDER EN VIE ========
@app.route("/")
def home():
    return "PulseAIbot est actif 😎"

# ============ LAUNCH ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
