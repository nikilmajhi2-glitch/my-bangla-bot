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

# --- RENDER KEEP-ALIVE SECTION ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------

# GET KEYS FROM ENVIRONMENT VARIABLES (SECURE)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

PROMPT = """
Tumi ekjon serious Bangladeshi customer support staff.
Boss jo kichhu Hindi ba English e bolbe seta ke tumi shudhu Bangla te (English letter e) translate korbe.
Kono emoji ba extra kotha bolbe na. Sirf clear polite Bangla likhbe.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("✓ Bot ready sir. Ab kuch bhi likhen.")
        print(f"✓ Started by user {update.effective_user.id}")
    except Exception as e:
        print(f"✗ Start error: {e}")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
        
    try:
        print(f"🤖 Generating...")
        response = model.generate_content(PROMPT + "\n\nBoss bolchen: " + text)
        bangla = response.text.strip()
        bangla = bangla.replace('**', '').replace('*', '')
            
        # Retry logic for sending
        max_retries = 5
        for attempt in range(max_retries):
            try:
                await update.message.reply_text(bangla)
                break
            except Exception:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
            
    except Exception as e:
        print(f"✗ Error: {e}")

async def main():
    print("🤖 Bot Starting...")
        
    # Connection settings for stability
    request = HTTPXRequest(connection_pool_size=1, connect_timeout=60, read_timeout=60)
        
    app_bot = Application.builder() \
        .token(TELEGRAM_TOKEN) \
        .request(request) \
        .build()
        
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
        
    await app_bot.initialize()
    await app_bot.start()
    await app_bot.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    keep_alive() # Starts the web server for Render
    try:
        asyncio.run(main()) # Starts the bot
    except KeyboardInterrupt:
        pass
