# bot.py
import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import google.generativeai as genai
import asyncio
import os
from flask import Flask
from threading import Thread
import sys

# Force logs to show immediately
sys.stdout.reconfigure(line_buffering=True)

# --- RENDER KEEP-ALIVE ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIG ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not TELEGRAM_TOKEN or not GEMINI_KEY:
    print("❌ ERROR: API Keys are missing in Render Environment Variables!")
        
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

PROMPT = """
Tumi ekjon serious Bangladeshi customer support staff.
Translate input to Bangla (English letters). No emojis.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✓ Bot is Online!")
    print(f"✓ /start command received from {update.effective_user.first_name}")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"📩 Message received: {text}") # Debug Message
        
    try:
        response = model.generate_content(PROMPT + "\n\nInput: " + text)
        bangla = response.text.strip().replace('*', '')
        await update.message.reply_text(bangla)
        print("✓ Reply sent successfully")
    except Exception as e:
        print(f"❌ Error generating/sending: {e}")
        await update.message.reply_text("⚠️ Error: Please try again.")

async def main():
    print("="*30)
    print("🤖 INITIALIZING BOT...")
    print("="*30)

    request = HTTPXRequest(connection_pool_size=1, connect_timeout=60, read_timeout=60)
        
    app_bot = Application.builder().token(TELEGRAM_TOKEN).request(request).build()
        
    # --- CONNECTION CHECK ---
    print("📡 Connecting to Telegram...")
    await app_bot.initialize()
    bot_identity = await app_bot.bot.get_me()
    print(f"✅ LOGGED IN SUCCESSFULLY AS: @{bot_identity.username}")
    print("="*30)
        
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
        
    await app_bot.start()
    await app_bot.updater.start_polling(drop_pending_updates=True)
    print("👂 Listening for messages...")
        
    await asyncio.Event().wait()

if __name__ == "__main__":
    keep_alive()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
