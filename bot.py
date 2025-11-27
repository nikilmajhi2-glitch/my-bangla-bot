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

# --- YOUR KEYS (HARDCODED) ---
TELEGRAM_TOKEN = "8508179051:AAH_hYMkwjT6g-csu6dnEdZuExSZGZ9T0SY"
GEMINI_KEY = "AIzaSyCtFBsHCffIhCxlyVqLfHXhVBdERQHe-dY"

# --- WEB SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is online with hardcoded keys!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT SETUP ---
# Configure Gemini
try:
    genai.configure(api_key=GEMINI_KEY)
    # Using 'gemini-pro' because it is the most compatible model
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Gemini Config Error: {e}")

PROMPT = """
Tumi ekjon serious Bangladeshi customer support staff.
Boss jo kichhu Hindi ba English e bolbe seta ke tumi shudhu Bangla te (English letter e) translate korbe.
Kono emoji ba extra kotha bolbe na. Sirf clear polite Bangla likhbe.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✓ Bot is Ready (Hardcoded Keys)")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"📩 Received: {text}")
    
    try:
        # Generate response
        response = model.generate_content(PROMPT + "\n\nInput: " + text)
        # Clean text
        bangla = response.text.strip().replace('*', '')
        
        # Send to Telegram
        await update.message.reply_text(bangla)
        print("✓ Sent reply")
    except Exception as e:
        print(f"❌ Error: {e}")
        await update.message.reply_text("⚠️ Error processing request. Keys might be invalid.")

async def main():
    print("🤖 Bot Starting...")
    
    # Network settings
    request = HTTPXRequest(connection_pool_size=1, connect_timeout=60, read_timeout=60)
    
    try:
        app_bot = Application.builder().token(TELEGRAM_TOKEN).request(request).build()
        
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
        
        print("📡 Connecting to Telegram...")
        await app_bot.initialize()
        await app_bot.start()
        
        # drop_pending_updates=True fixes the conflict error slightly
        await app_bot.updater.start_polling(drop_pending_updates=True)
        print("✅ Polling Started!")
        
        await asyncio.Event().wait()
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    keep_alive() # Start Render Server
    try:
        asyncio.run(main()) # Start Bot
    except KeyboardInterrupt:
        pass


