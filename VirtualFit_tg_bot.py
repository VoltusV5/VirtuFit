from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv 
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands="start"))
async def start_command(message: Message):
    await message.answer("Привет! Я бот VirtualFit.\n") #Сюда надо придумать что написать, это когда пользователь первый раз заходит


@dp.message(Command(commands="help"))
async def start_command(message: Message):
    await message.answer("Отправь мне фотографию одежды,"
    " а я сделаю тебе короткий ролик с 3д моделькой одетой в одежду с фото!:)") 

#Основная функция вот тут будет всё происходить с блендером...
@dp.message(F.photo)
async def photo_processing(message: Message):
    await message.reply_photo(message.photo[0].file_id) #Пока что работает как эхо


@dp.message()
async def other_message(message:Message):
    await message.answer("Пока что я ничего не умею, как Тамир(не обижайся братик), приходи позже или отправь мне фото)")


if __name__=='__main__':
    dp.run_polling(bot)