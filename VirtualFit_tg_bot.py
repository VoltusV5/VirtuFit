from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message, KeyboardButton, BotCommand
from aiogram.types import Message, KeyboardButton
from dotenv import load_dotenv 
from sqlalchemy.orm import Session
from database import *
import os


Base.metadata.create_all(bind=engine)

def get_db():
    db:Session = SessionLocal()
    return db

    try:
        yield db
    finally:
        db.close()



load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

#Создём кнопки


kb_builder1 = ReplyKeyboardBuilder()
kb_builder_menu = ReplyKeyboardBuilder()
buttons_1 = [KeyboardButton(text="Футболка"), KeyboardButton(text="Кофта")]
buttons_menu = [KeyboardButton(text="Подписка"), KeyboardButton(text="Ввести размеры"), KeyboardButton(text="...")]
kb_builder1.row(*buttons_1, width=2)
kb_builder_menu.row(*buttons_menu, width=2)


async def set_main_menu(bot:Bot):
    menu_commands = [
        BotCommand(command='/menu', description="Открыть меню"),
        BotCommand(command='/help', description='Справка по работе бота')             
        ]
    await bot.set_my_commands(menu_commands)

dp.startup.register(set_main_menu)



kb_builder = ReplyKeyboardBuilder()

button = [KeyboardButton(text="Футболка"), KeyboardButton(text="Кофта")]

kb_builder.row(*button, width=2)


@dp.message(Command(commands="start"))
async def start_command(message: Message):
    db = get_db()
    person = Person(id=message.from_user.id, photo=False)
    db.add(person)
    db.commit()
    db.refresh(person)

    db.close()

    await message.answer("Привет! Я бот VirtualFit.\n") #Сюда надо придумать что написать, это когда пользователь первый раз заходит
    

@dp.message(Command(commands="help"))
async def start_command(message: Message):
    await message.answer("Отправь мне фотографию одежды,"
    " а я сделаю тебе короткий ролик с 3д моделькой одетой в одежду с фото!:)") 



@dp.message(F.text == "Ввести размеры")
async def size_people(message:Message):
    '''Надо придумать как забрать размеры'''

@dp.message(Command(commands='menu'))
async def start_command(message: Message):
    await message.answer("Что будем делать?)", reply_markup=kb_builder_menu.as_markup(resize_keyboard=True))
    


#Основная функция вот тут будет всё происходить с блендером...
@dp.message(F.photo)
async def photo_processing(message: Message):
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"photo/{message.from_user.id}.jpg")

    await bot.download_file(file_path, f"photo/photo_before/{message.from_user.id}.jpg")

    db = get_db()
    person = db.get(Person, message.from_user.id)
    person.photo = True
    db.commit()
    db.close()
    await message.answer(text="Какая одежда изображена на фото?",
                         reply_markup= kb_builder1.as_markup(resize_keyboard=True, one_time_keyboard=True))
    await message.answer(text="Какая одежда изображена на фото?",
                         reply_markup= kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True))


@dp.message(F.text == "Футболка")
async def t_short(message: Message):
    db = get_db()
    person = db.get(Person, message.from_user.id)
    if person.photo:
        '''Тут надо сделать реализацию скрипта блендера и всей суты нашей'''
        person.photo = False
        db.commit()

        db.close()

        await message.answer("Когда нибудь я научусь делать 3д видео:(((")
    else:
        await message.answer("Вы не отправили фото")


@dp.message()
async def other_message(message:Message):
    await message.answer("Пока что я ничего не умею, как Тамир(не обижайся братик), приходи позже или отправь мне фото)")



if __name__=='__main__':
    dp.run_polling(bot)
