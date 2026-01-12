from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests

BOT_TOKEN = "8117998371:AAHNKV2FWzK27ahEh9qkLhQI1RoQQED6Ln8"  # Replace with your real token TELEBOT
CENTRAL_PARSER_URL = "http://127.0.0.1:5000/command"  # Update this if needed CENTRAL PARSER

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " Welcome to DCDPOS!\n\n"
        "Just type commands like:\n"
        " Open Figma on a\n"
        " Take screenshot on a\n"
        "AI will understand and execute it on your devices!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text
    try:
        response = requests.post(CENTRAL_PARSER_URL, json={"command": command}, timeout=30)
        result = response.json()

        if "generated_code" in result:
            device_status = result.get('device_response', {})
            if isinstance(device_status, dict):
                status = device_status.get('status', 'Executed')
            else:
                status = str(device_status)
            
            reply = (
                f"✅ Command Executed!\n\n"
                f"📝 Command: {command}\n"
                f"📊 Status: {status}"
            )
        elif "error" in result:
            error_msg = str(result['error']).replace('_', ' ').replace('*', ' ').replace('`', ' ')
            reply = f"Error: {error_msg}"
        else:
            reply = f"Response: {str(result)}"

        await update.message.reply_text(reply)
    except requests.exceptions.Timeout:
        await update.message.reply_text("Request timed out. Is the Central Parser running?")
    except requests.exceptions.ConnectionError:
        await update.message.reply_text("Connection failed. Is the Central Parser running at " + CENTRAL_PARSER_URL + "?")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
