from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Календарь")],
        [KeyboardButton(text="🌱 Добавить растение")],
        [KeyboardButton(text="✏ Изменить график полива")]
    ],
    resize_keyboard=True
)

calendar_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сегодня"), KeyboardButton(text="Неделя")],
        [KeyboardButton(text="⬅ Назад")]
    ],
    resize_keyboard=True
)

def generate_edit_menu(plants):
    buttons = []
    for p in plants:
        buttons.append([
            InlineKeyboardButton(
                text=f"{p['name']} ({p['interval']} дн.)",
                callback_data=f"edit_{p['id']}"
            ),
            InlineKeyboardButton(
                text="❌",
                callback_data=f"delete_{p['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
