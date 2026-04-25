import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8252652513:AAFZzev9FqdknCzNhHhBoQPUov079ZMpaIs"
BOT_USERNAME = "watanivedios_bot"  

CHANNELS = [
    ("Crypto Channel", "@cryptotrader0022"),
    ("Second channel", "@watanjan77"),
]

VIDEOS = {}
VIDEO_COUNTER = 1


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()


def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


async def is_joined(context, user_id):
    for name, channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True


def join_keyboard(video_code):
    keyboard = []

    for name, channel in CHANNELS:
        keyboard.append([
            InlineKeyboardButton(
                f"📢 Join {name}",
                url=f"https://t.me/{channel.replace('@', '')}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("✅ ما Join وکړ / Check", callback_data=f"check:{video_code}")
    ])

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        video_code = context.args[0]
    else:
        await update.message.reply_text("ویډیو لینک ناسم دی یا ویډیو نشته.")
        return

    if video_code not in VIDEOS:
        await update.message.reply_text("دا ویډیو ونه موندل شوه یا لینک زوړ دی.")
        return

    await update.message.reply_text(
        "د ویډیو د لیدلو لپاره لومړی دا چینلونه Join کړه 👇",
        reply_markup=join_keyboard(video_code)
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    video_code = data.split(":")[1]

    user_id = query.from_user.id

    if video_code not in VIDEOS:
        await query.message.reply_text("دا ویډیو ونه موندل شوه.")
        return

    if await is_joined(context, user_id):
        sent = await context.bot.send_video(
            chat_id=user_id,
            video=VIDEOS[video_code],
            caption="🎬 دا ویډیو یوازې 60 ثانیې ښکاري."
        )

        await query.message.reply_text("✅ ویډیو خلاصه شوه. 60 ثانیې وروسته به حذف شي.")

        await asyncio.sleep(60)

        try:
            await context.bot.delete_message(
                chat_id=user_id,
                message_id=sent.message_id
            )
        except Exception:
            pass

    else:
        await query.message.reply_text(
            "❌ ته لا ټولو چینلونو ته Join نه یې. اول Join کړه، بیا Check ووهه."
        )


async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global VIDEO_COUNTER

    file_id = update.message.video.file_id
    video_code = f"v{VIDEO_COUNTER}"
    VIDEO_COUNTER += 1

    VIDEOS[video_code] = file_id

    video_link = f"https://t.me/{BOT_USERNAME}?start={video_code}"

    await update.message.reply_text(
        f"✅ ویډیو ثبت شوه.\n\n"
        f"دا لینک په خپل چینل کې پوسټ کړه 👇\n\n"
        f"{video_link}"
    )


threading.Thread(target=run_server, daemon=True).start()

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check, pattern="^check:"))
app.add_handler(MessageHandler(filters.VIDEO, save_video))

app.run_polling()