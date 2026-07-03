import os
import json
import logging
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ChatMemberUpdated,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]          # токен берём из переменной окружения Railway
PHOTO_PATH = "photo.jpg"                      # картинка, которую бот отправляет
WEBAPP_URL = "https://htx-six.vercel.app/"

# Ваш личный Telegram ID — только у вас будет доступ к команде /post
# Узнать свой ID можно у бота @userinfobot
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

CHATS_FILE = "chats.json"


def load_chats() -> dict:
    if os.path.exists(CHATS_FILE):
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_chats(chats: dict):
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Открыть обучение📖", url=WEBAPP_URL)]
    ])
    with open(PHOTO_PATH, "rb") as photo:
        await update.message.reply_photo(photo=photo, reply_markup=keyboard)


async def track_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запоминаем каждый чат (группу/канал), куда добавили бота."""
    result: ChatMemberUpdated = update.my_chat_member
    chat = result.chat
    new_status = result.new_chat_member.status

    chats = load_chats()

    if new_status in ("member", "administrator", "creator"):
        chats[str(chat.id)] = {
            "title": chat.title or chat.full_name or str(chat.id),
            "type": chat.type,
        }
        save_chats(chats)
    elif new_status in ("left", "kicked"):
        chats.pop(str(chat.id), None)
        save_chats(chats)


async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /post — только для админа. Показывает панель выбора чата."""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    chats = load_chats()
    if not chats:
        await update.message.reply_text(
            "Бот пока не состоит ни в одной группе или канале.\n"
            "Добавьте бота администратором в нужный чат и попробуйте снова."
        )
        return

    buttons = [
        [InlineKeyboardButton(
            text=f"{info['title']} ({'канал' if info['type'] == 'channel' else 'группа'})",
            callback_data=f"sendpost:{chat_id}"
        )]
        for chat_id, info in chats.items()
    ]

    await update.message.reply_text(
        "Выберите, куда отправить пост:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def handle_post_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ У вас нет доступа.")
        return

    chat_id = query.data.split(":", 1)[1]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Открыть обучение📖", url=WEBAPP_URL)]
    ])

    try:
        with open(PHOTO_PATH, "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                reply_markup=keyboard
            )
        await query.edit_message_text("✅ Пост отправлен.")
    except Exception as e:
        await query.edit_message_text(f"❌ Не удалось отправить: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(CallbackQueryHandler(handle_post_choice, pattern=r"^sendpost:"))
    app.add_handler(ChatMemberHandler(track_chat, ChatMemberHandler.MY_CHAT_MEMBER))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
