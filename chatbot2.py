import requests
import json
import os
import time
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)

# 🔐 KEYS (REPLACE THESE)
TELEGRAM_BOT_TOKEN = "8243958265:AAFaGjKbMEujhu2nySGfqXoMwNBnIyKuq6c"
GEMINI_API_KEY = "AIzaSyBBgATdrX1Vpk1--FNjFcetuQSeAfux77c"

# 👋 WELCOME MESSAGE
WELCOME_MESSAGE = """
👋 Hey there! I’m AbbayGPT 🤖✨

Your smart AI buddy for 💻 coding, 🛡️ cybersecurity, and 🚀 learning tech.

Let’s build something powerful together ⚡🔥
"""

# 🧠 MEMORY SYSTEM
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        return json.load(open(MEMORY_FILE))
    return {}

def save_memory(data):
    json.dump(data, open(MEMORY_FILE, "w"))

memory = load_memory()
# 🤖 MODELS (AUTO SWITCH)
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-pro-latest"
]

# 💻 GEMINI FUNCTION
def ask_gemini(prompt):
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"

        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()

            print(f"[{model}] RESPONSE:", result)

            if "candidates" in result:
                return result["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            print(f"[{model}] ERROR:", e)

        time.sleep(1)

    return "⚡ AbbayGPT is busy right now. Try again later."

# 👋 /START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)

# 📩 MESSAGE HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    user_text = update.message.text

    # 🧠 SAVE MEMORY
    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append(user_text)
    memory[user_id] = memory[user_id][-10:]
    save_memory(memory)

    # 📚 CONTEXT
    history = "\n".join(memory[user_id])

    prompt = f"""
You are AbbayGPT 🤖.
You are a highly intelligent assistant specialized in:
- Programming 💻
- Debugging 🐞
- Cybersecurity & Ethical Hacking 🛡️ (legal only)

IMPORTANT RULES:
- If asked about owner: "My owner is Vexon, a powerful programmer and cybersecurity enthusiast."
- Be smooth, clear, and helpful.

Conversation history:
{history}

User: {user_text}
"""

    # ⌨️ typing effect
    await update.message.chat.send_action(action="typing")

    # 🤖 AI RESPONSE
    reply = ask_gemini(prompt)

    # 📤 SEND RESPONSE
    await update.message.reply_text(reply)

# 🚀 MAIN BOT
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 AbbayGPT starting...")

    app.run_polling(
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
