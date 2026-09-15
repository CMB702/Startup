import os
import logging
import threading
import asyncio
import time
import requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """Tum ek business mentor AI ho jiska naam "BizGuru" hai. Tumhara kaam SIRF business se related baaton me help karna hai:
- Business ideas dena (trending, low-investment, high-profit)
- Business plan banane me madad
- Marketing, sales, finance, legal basics samjhana
- Startup se related problems solve karna
- Competitor analysis, pricing strategy, growth tips dena

RULES:
1. Agar user business se alag topic pe baat kare (movies, cricket, personal life, politics, etc), toh politely mana kar do aur bolo "Main sirf business topics pe hi baat karta hoon bhai! Business se related kuch pucho." Phir ek related business question suggest karo.
2. Hamesha practical, actionable advice do — generic gyaan mat do.
3. Hindi-English mix (Hinglish) me baat karo, friendly aur "bhai" wale tone me, jaisa ek dost business advice deta hai.
4. Jab user business idea maange, unki location, budget, interest puchke personalized idea do.
5. Short aur clear replies do, lambi lecture mat do jab tak user detail na maange.
"""

# Simple in-memory chat history per user (resets if bot restarts)
user_history = {}

def ask_gemini(user_id, message, retries=3):
    history = user_history.get(user_id, [])
    history.append({"role": "user", "parts": [{"text": message}]})

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": history,
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 700}
    }

    reply = None
    for attempt in range(retries):
        try:
            resp = requests.post(GEMINI_URL, json=payload, timeout=30)
            if resp.status_code == 503:
                # Google's servers are temporarily overloaded, retry after a short wait
                logging.warning(f"Gemini 503, retrying ({attempt+1}/{retries})...")
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            data = resp.json()
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            break
        except Exception as e:
            logging.error(f"Gemini error: {e}")
            if attempt == retries - 1:
                return "Bhai Google ke servers abhi thode busy hain, thodi der me dobara try karo."

    if reply is None:
        return "Bhai Google ke servers abhi thode busy hain, thodi der me dobara try karo."

    history.append({"role": "model", "parts": [{"text": reply}]})
    # keep last 20 messages only to avoid growing too large
    user_history[user_id] = history[-20:]
    return reply


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste bhai! Main BizGuru hoon 💼\n\n"
        "Main sirf aur sirf business ki baat karta hoon:\n"
        "• Naye business ideas\n"
        "• Business plan banana\n"
        "• Marketing/sales tips\n"
        "• Funding, pricing, growth strategy\n\n"
        "Bas apna sawaal poochho! Ya /idea likho, main ek business idea suggest karunga."
    )


async def idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    reply = ask_gemini(user_id, "Mujhe ek trending, low-investment business idea suggest karo India ke context me. Pehle mujhse budget aur interest puchho.")
    await update.message.reply_text(reply)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_history.pop(user_id, None)
    await update.message.reply_text("Chat history clear kar di bhai, fresh start karte hain!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = ask_gemini(user_id, text)
    await update.message.reply_text(reply)


# --- Health check web server (so Render treats this as a free "Web Service") ---
flask_app = Flask(__name__)


@flask_app.route("/")
def health():
    return "BizGuru bot is alive!"


def run_bot():
    # Background threads don't get an asyncio event loop automatically in
    # modern Python, so we create and attach one before starting the bot.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("idea", idea))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot chal raha hai...")
    # stop_signals=None: this runs in a background thread, and signal handlers
    # can only be registered on the main thread, so we skip that setup here.
    app.run_polling(stop_signals=None)


def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        raise SystemExit("TELEGRAM_TOKEN aur GEMINI_API_KEY environment variables set karo pehle!")

    # Bot polling runs in a background thread...
    threading.Thread(target=run_bot, daemon=True).start()

    # ...while Flask runs on the main thread, so Render detects the open port immediately.
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
