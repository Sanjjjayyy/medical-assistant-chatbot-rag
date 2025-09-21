# telegram_bot.py

import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FASTAPI_URL = os.getenv("FASTAPI_URL")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.message.chat_id
    logger.info(f"Received message from chat_id {chat_id}: {user_text}")

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        # --- UPDATED: Send the chat_id as the session_id ---
        payload = {
            "message": user_text,
            "session_id": str(chat_id)
        }
        response = requests.post(FASTAPI_URL, json=payload, timeout=120)
        
        if response.status_code == 200:
            bot_reply = response.json().get("reply", "No reply found.")
        else:
            logger.error(f"API returned status {response.status_code}: {response.text}")
            bot_reply = "Sorry, my brain is not working right now."
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not connect to the FastAPI server: {e}")
        bot_reply = "I'm having trouble connecting to my knowledge base."

    await update.message.reply_text(bot_reply)

def main():
    if not TELEGRAM_TOKEN or not FASTAPI_URL:
        logger.error("Missing TELEGRAM_TOKEN or FASTAPI_URL in .env file.")
        return

    logger.info("Starting Telegram bot with memory...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    logger.info("Bot is polling for updates...")
    app.run_polling()

if __name__ == "__main__":
    main()