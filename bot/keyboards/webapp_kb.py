from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu(webapp_url: str):
    builder = InlineKeyboardBuilder()

    # Красивая кнопка Web App
    builder.row(
        InlineKeyboardButton(
            text="🎨 Открыть интерактивную галерею",
            web_app=WebAppInfo(url=f"{webapp_url}/webapp")
        )
    )

    # Дополнительные кнопки
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
        InlineKeyboardButton(text="🏆 Топ участников", callback_data="top_users")
    )

    builder.row(
        InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
        InlineKeyboardButton(text="📸 Мои фото", callback_data="my_photos")
    )

    return builder.as_markup()