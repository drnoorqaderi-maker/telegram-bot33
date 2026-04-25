from telegram.ext import MessageHandler, filters

async def get_video_id(update, context):
    await update.message.reply_text(update.message.video.file_id)

app.add_handler(MessageHandler(filters.VIDEO, get_video_id))
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# دا server په background کې چلوه
threading.Thread(target=run_server).start()
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8252652513:AAEuyBA0T7CDri6zf68FYGfE4yBC3ij2bgs"

CHANNELS = [
    ("https://t.me/cryptotrader0022"),
    ("https://t.me/jdjejdbsk"),
]

VIDEO_FILE_ID = "YOUR_VIDEO_FILE_ID"

async def is_joined(context, user_id):
    for name, channel in CHANNELS:
        member = await context.bot.get_chat_member(channel, user_id)
        if member.status not in ["member", "administrator", "creator"]:
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    for name, channel in CHANNELS:
        keyboard.append([InlineKeyboardButton(f"📢 Join {name}", url=f"https://t.me/{channel.replace('@','')}")])

    keyboard.append([InlineKeyboardButton("✅ Check", callback_data="check")])

    await update.message.reply_text(
        "اول دا چینلونه Join کړه 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if await is_joined(context, user_id):
        await query.message.reply_text("✅ Done، ویډیو درته راځي...")
        await context.bot.send_video(chat_id=user_id, video=VIDEO_FILE_ID)
    else:
        await query.message.reply_text("❌ ټول چینلونه Join کړه بیا Check ووهه")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check, pattern="check"))

app.run_polling()