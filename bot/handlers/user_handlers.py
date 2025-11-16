from aiogram import Router, F
from aiogram.types import Message, WebAppInfo
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config
from database import db

router = Router()


def get_main_menu():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🎨 Открыть интерактивную галерею",
        web_app=WebAppInfo(url=f"{config.WEBAPP_URL}/webapp")
    )

    builder.button(text="📊 Статистика", callback_data="stats")
    builder.button(text="❓ Помощь", callback_data="help")

    builder.adjust(1)  # По одной кнопке в ряд
    return builder.as_markup()


@router.message(Command("start"))
async def cmd_start(message: Message):
    # Сохраняем пользователя в базу
    if db:
        db.users.update_one(
            {'user_id': message.from_user.id},
            {'$set': {
                'username': message.from_user.username,
                'full_name': message.from_user.full_name,
                'first_seen': message.date
            }},
            upsert=True
        )

    await message.answer(
        "🎨 <b>Добро пожаловать в Graffiti Wall!</b>\n\n"
        "Это интерактивная стена, где каждый может оставить свой след:\n"
        "• 📸 Отправляй фото чтобы добавить на стену\n"
        "• 🎨 Смотри общую галерею в Web App\n"
        "• ❤️ Ставь лайки понравившимся работам\n\n"
        "<i>Нажми кнопку ниже чтобы открыть галерею:</i>",
        reply_markup=get_main_menu()
    )


@router.message(F.photo)
async def handle_photo(message: Message):
    if not db:
        await message.answer("❌ База данных не подключена")
        return

    # Сохраняем информацию о фото
    photo_data = {
        'user_id': message.from_user.id,
        'username': message.from_user.username or message.from_user.first_name,
        'telegram_file_id': message.photo[-1].file_id,
        'position_x': 100,  # Пока фиксированная позиция
        'position_y': 100,
        'likes': 0,
        'liked_by': [],
        'created_at': message.date
    }

    db.photos.insert_one(photo_data)

    await message.answer(
        f"✅ <b>Фото добавлено на стену!</b>\n\n"
        f"👤 Автор: {photo_data['username']}\n"
        f"📍 Позиция: {photo_data['position_x']}, {photo_data['position_y']}\n"
        f"📸 Всего фото на стене: {db.photos.count_documents({})}\n\n"
        f"<i>Открой галерею чтобы увидеть свою работу!</i>",
        reply_markup=get_main_menu()
    )