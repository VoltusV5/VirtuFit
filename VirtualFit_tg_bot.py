from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message, KeyboardButton
from dotenv import load_dotenv 
import os

users = {}

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

#Создём кнопки

kb_builder = ReplyKeyboardBuilder()

button = [KeyboardButton(text="Футболка"), KeyboardButton(text="Кофта")]

kb_builder.row(*button, width=2)

@dp.message(Command(commands="start"))
async def start_command(message: Message):
    await message.answer("Привет! Я бот VirtualFit.\n") #Сюда надо придумать что написать, это когда пользователь первый раз заходит
    if message.from_user.id not in users:
        users[message.from_user.id] = {
            "Photo": False
            }

@dp.message(Command(commands="help"))
async def start_command(message: Message):
    await message.answer("Отправь мне фотографию одежды,"
    " а я сделаю тебе короткий ролик с 3д моделькой одетой в одежду с фото!:)") 


#Основная функция вот тут будет всё происходить с блендером...
@dp.message(F.photo)
async def photo_processing(message: Message):
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"photo/photo_before/{message.from_user.id}.jpg")
    users[message.from_user.id]["Photo"] = True
    await message.answer(text="Какая одежда изображена на фото?",
                         reply_markup= kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True))

@dp.message(F.text == "Футболка")
async def t_short(message: Message):
    if users[message.from_user.id]["Photo"]:
        '''Тут надо сделать реализацию скрипта блендера и всей суты нашей'''
        users[message.from_user.id]["Photo"] = False
        await message.answer("Когда нибудь я научусь делать 3д видео:(((")
    else:
        users[message.from_user.id]["Photo"] = False
        await message.answer("Вы не отправили фото")


@dp.message()
async def other_message(message:Message):
    await message.answer("Пока что я ничего не умею, как Тамир(не обижайся братик), приходи позже или отправь мне фото)")


if __name__=='__main__':
    dp.run_polling(bot)
