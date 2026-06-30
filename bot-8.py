import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]  # берём токен из переменной окружения Railway
PHOTO_PATH = "photo.jpg"             # путь к картинке, которую бот будет отправлять
WEBAPP_URL = "https://habotlola-gif.github.io/htx/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text="Открыть обучение📖",
            url=WEBAPP_URL
        )]
    ])

    with open(PHOTO_PATH, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            reply_markup=keyboard
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()
