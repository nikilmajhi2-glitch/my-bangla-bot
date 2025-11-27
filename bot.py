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

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8508179051:AAH_hYMkwjT6g-csu6dnEdZuExSZGZ9T0SY"

# Your 4 API Keys
API_KEYS = [
    "AIzaSyC2ZjTc8ROvIsl0M3a-T8SqSNvqx3PZKps",
    "AIzaSyB_Hp5b6g5tiyOvJn6kUN8uCwk6SOeyP_k",
    "AIzaSyCjqmVPTzlNPLuTzzAomu1-nsLHNoIljaM",
    "AIzaSyB8bvtSKIouzR7vvcCeoSy1OZGlxPNMpVk"
]

# All Free-Tier Eligible Models (Ordered by Priority)
MODELS = [
    "gemini-2.0-flash-exp",  # Newest/Fastest
    "gemini-1.5-flash",      # Standard Reliable
    "gemini-1.5-flash-8b",   # Ultra Lightweight
    "gemini-1.5-pro",        # High Intelligence
    "gemini-pro"             # Legacy Fallback
]

PROMPT = """
Tumi ekjon serious Bangladeshi customer support staff.
Translate the input to clear Bangla (using English letters/Banglish).
No emojis. Be polite.
"""

# --- WEB SERVER ---
app = Flask('')

@app.route('/')
def home():
    return f"Ultimate Bot Online! {len(API_KEYS)} Keys x {len(MODELS)} Models."

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ULTIMATE ROTATION LOGIC ---
def get_response_with_rotation(text):
    full_prompt = PROMPT + "\n\nInput: " + text
    
    # Loop 1: Cycle through API Keys
    for key_index, api_key in enumerate(API_KEYS):
        # print(f"🔑 Key #{key_index + 1} Active")
        genai.configure(api_key=api_key)
        
        # Loop 2: Cycle through Models for the active Key
        for model_name in MODELS:
            try:
                # print(f"  👉 Attempting: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                
                result = response.text.strip().replace('*', '')
                if result:
                    return result # Success! Return immediately.
                    
            except Exception as e:
                # Log failures silently and continue to next model
                print(f"    ⚠️ Fail: Key {key_index+1} | {model_name} -> {e}")
                continue
    
    print("❌ FATAL: All Keys and Models Failed.")
    return None

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✓ Bot Ready! (Max Reliability Mode)")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"📩 User: {text}")
    
    bangla = get_response_with_rotation(text)
    
    if bangla:
        await update.message.reply_text(bangla)
        print("✓ Sent Reply")
    else:
        await update.message.reply_text("⚠️ System Busy. All API keys exhausted. Try again in 1 min.")

async def main():
    print("🤖 Bot Starting with ULTIMATE ROTATION...")
    request = HTTPXRequest(connection_pool_size=1, connect_timeout=60, read_timeout=60)
    
    try:
        app_bot = Application.builder().token(TELEGRAM_TOKEN).request(request).build()
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
        
        print("📡 Connecting...")
        await app_bot.initialize()
        await app_bot.start()
        await app_bot.updater.start_polling(drop_pending_updates=True)
        
        print("✅ System Active")
        await asyncio.Event().wait()
    except Exception as e:
        print(f"❌ STARTUP ERROR: {e}")

if __name__ == "__main__":
    keep_alive()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass



