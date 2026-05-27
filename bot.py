import os
import json
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from apscheduler.schedulers.background import BackgroundScheduler

# ---------------- LOAD ENV ---------------- #

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
PHOTO_DIR = os.getenv("PHOTO_DIR")
DB_FILE = os.getenv("DB_FILE")

# ---------------- CONFIG ---------------- #

DATA_FILE = DB_FILE

scheduler = BackgroundScheduler()

# Create DB folder if not exists
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# ---------------- DATABASE ---------------- #

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {"users": {}}


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- MINUTES ---------------- #

ALL_MINUTES = []

# Allowed hours: 7 AM -> 11:59 PM
for h in range(7, 24):
    for m in range(60):
        ALL_MINUTES.append(f"{h:02d}:{m:02d}")


def get_random_unused_minute(user_id):
    used = data["users"][str(user_id)]["used_minutes"]

    remaining = [m for m in ALL_MINUTES if m not in used]

    if not remaining:
        return None

    return random.choice(remaining)


# ---------------- SEND MESSAGE ---------------- #

async def send_capture_message(application, chat_id, minute):
    await application.bot.send_message(
        chat_id=chat_id,
        text=f"Capture this moment 📸\n\nMinute: {minute}"
    )


# ---------------- SCHEDULER ---------------- #

def schedule_next_capture(application, user_id, chat_id):
    minute = get_random_unused_minute(user_id)

    if not minute:
        return

    hour, minute_num = map(int, minute.split(":"))

    now = datetime.now()

    run_time = now.replace(
        hour=hour,
        minute=minute_num,
        second=0,
        microsecond=0
    )

    # If time already passed today -> tomorrow
    if run_time <= now:
        run_time += timedelta(days=1)

    scheduler.add_job(
        lambda: application.create_task(
            send_capture_message(application, chat_id, minute)
        ),
        "date",
        run_date=run_time,
    )

    data["users"][str(user_id)]["current_minute"] = minute

    save_data()

    print(f"Scheduled {minute} for user {user_id}")


# ---------------- START ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    user_id = str(user.id)

    # Create user if not exists
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "used_minutes": [],
            "entries": [],
            "current_minute": None
        }

    save_data()

    # Create user photo folder
    os.makedirs(f"{PHOTO_DIR}/{user_id}", exist_ok=True)

    # First photo = NOW
    current_time = datetime.now().strftime("%H:%M")

    data["users"][user_id]["current_minute"] = current_time

    save_data()

    await update.message.reply_text(
        f"First capture starts NOW 📸\n\nSend a photo."
    )

    # Schedule next random moment
    schedule_next_capture(
        context.application,
        user_id,
        update.effective_chat.id
    )


# ---------------- PHOTO HANDLER ---------------- #

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    user_id = str(user.id)

    # Ignore if user not started
    if user_id not in data["users"]:
        await update.message.reply_text(
            "Please start the bot first using /start"
        )
        return

    minute = data["users"][user_id]["current_minute"]

    photo = update.message.photo[-1]

    file = await context.bot.get_file(photo.file_id)

    filename = f"{datetime.now().timestamp()}.jpg"

    # Create user folder if missing
    user_folder = f"{PHOTO_DIR}/{user_id}"

    os.makedirs(user_folder, exist_ok=True)

    path = f"{user_folder}/{filename}"

    # Download image
    await file.download_to_drive(path)

    # Save DB entry
    data["users"][user_id]["entries"].append({
        "minute": minute,
        "date": str(datetime.now()),
        "photo": path
    })

    # Save used minute
    if minute not in data["users"][user_id]["used_minutes"]:
        data["users"][user_id]["used_minutes"].append(minute)

    save_data()

    await update.message.reply_text(
        "Moment saved successfully ✅"
    )


# ---------------- MAIN ---------------- #

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

scheduler.start()

print("Bot running...")

app.run_polling()
