from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton



kb_builder1 = ReplyKeyboardBuilder()
kb_builder_menu = ReplyKeyboardBuilder()
kb_builder_payments = ReplyKeyboardBuilder()
kb_builder = ReplyKeyboardBuilder()
buttons_1 = [KeyboardButton(text="Футболка"), KeyboardButton(text="Кофта")]
buttons_menu = [KeyboardButton(text="📏Ввести размеры📏"), 
                KeyboardButton(text="ⓘЧто умеешь?ⓘ"), 
                KeyboardButton(text="🥼Примерить одежду🔧"),
                KeyboardButton(text="📝Мои размеры📝")
                ]

button_b2b_b2c = [KeyboardButton(text="🙂Пользователь🙂"), KeyboardButton(text="💼Бизнес💼")]



button = [KeyboardButton(text="Футболка"), KeyboardButton(text="Кофта")]
kb_builder.row(*button, width=2)
kb_builder1.row(*buttons_1, width=2)
kb_builder_menu.row(*buttons_menu, width=2)
kb_builder_payments.row(*button_b2b_b2c, width=2)