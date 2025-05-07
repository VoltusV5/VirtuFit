from aiogram import Bot, Dispatcher, F
import asyncio
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state,State,StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, BotCommand, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from dotenv import load_dotenv 
from sqlalchemy.orm import Session
from control_size import control
from buttons import kb_builder1, kb_builder_menu, kb_builder_payments, kb_builder
import time
from database import *
import os

         
        
Base.metadata.create_all(bind=engine)

def get_db():
    db:Session = SessionLocal()
    return db

storage = MemoryStorage()



load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


class FSMform(StatesGroup):
    gender = State() #Пол
    chest = State() #Обхват груди
    waist = State() #Талия
    hips = State() #Бёдра
    shoulder_width = State() #ширина плечь
    height = State() #Рост
    chest_girl = State() # Размер груди
    neck = State() #Шея
    massa = State()
    len_arm = State() #Длинна рук


async def set_main_menu(bot:Bot):
    menu_commands = [
        BotCommand(command='/menu', description="Открыть меню"),
        BotCommand(command='/help', description='Справка по работе бота'),
        BotCommand(command='/cancel', description="Отмена заполнения размеров")             
        ]
    await bot.set_my_commands(menu_commands)

dp.startup.register(set_main_menu)



@dp.message(Command(commands="start"), StateFilter(default_state))
async def start_command(message: Message):
    db = get_db()
    person = Person(id=message.from_user.id, photo=False)
    db.add(person)
    db.commit()
    db.refresh(person)

    db.close()

    await message.answer("Привет! Я бот VirtualFit.\n") #Сюда надо придумать что написать, это когда пользователь первый раз заходит
    

@dp.message(Command(commands="help"), StateFilter(default_state))
async def start_command(message: Message):
    await message.answer("Отправь мне фотографию одежды,"
    " а я сделаю тебе короткий ролик с 3д моделькой одетой в одежду с фото!:)") 

@dp.message(Command(commands="cancel"), StateFilter(default_state))
async def cancel_default(message: Message):
    await message.answer("Отменять нечего.")


@dp.message(Command(commands='menu'), StateFilter(default_state))
async def start_command(message: Message):
    await message.answer("Что будем делать?)", reply_markup=kb_builder_menu.as_markup(resize_keyboard=True))
    

@dp.message(Command(commands="cancel"), ~StateFilter(default_state))
async def cancel_form(message: Message, state: FSMContext):
    await message.answer("Вы вышли из заполнения размеров")
    await state.clear()

@dp.message(F.text == 'Ввести размеры', StateFilter(default_state))
async def start_form(message: Message, state: FSMContext):
    male_button = InlineKeyboardButton(
        text='Мужской ♂',
        callback_data='male'
    )
    female_button = InlineKeyboardButton(
        text='Женский ♀',
        callback_data='female'
    )
    keyboard = [[male_button, female_button]]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(
        text="👋 Привет! Давай знакомиться! Какой у тебя пол?\n\n"
"➤ Нажми «Мужской» или «Женский».\n\n"
"✨ Не стесняйся, я не расскажу! А если захочешь начать заново — /cancel.\n", 
        reply_markup=markup)
    await state.set_state(FSMform.gender)

@dp.callback_query(StateFilter(FSMform.gender), F.data.in_(['male', 'female']))
async def gender_done(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)

    await callback.message.delete()
    await callback.message.answer("📏 Твой рост в см? Не приуменьшай, я верю в тебя!\n\n"
"➤ Пример: *175*.\n\n"
"⚠️ Если запутался — команда /cancel !")
    await state.set_state(FSMform.height)

@dp.message(StateFilter(FSMform.gender))
async def gender_error(message: Message):
    await message.answer("😅 Ой, я тебя не понял! Давай еще разок: «Мужской» или «Женский»?\n\n"
"➤ P.S. Всегда можно сбежать через /cancel!")

@dp.message(StateFilter(FSMform.height), control)
async def height_done(ms:Message, state: FSMContext):
    await state.update_data(height=int(ms.text))
    await ms.answer("Отлично!\n📦 Теперь измерь грудь (по самой широкой части в обхвате)!\n\n"
                    "➤ Напиши число, например: *98*. Это останется между нами 🤫\n\n"
                    "⚠️ Застрял? Смело пиши /cancel!")
    await state.set_state(FSMform.chest)

@dp.message(StateFilter(FSMform.height))
async def height_error(ms:Message):
     await ms.answer("❌ Кажется, что-то не то! Попробуй еще раз!\n\n"
"➤ Пример: *85*. И помни: /cancel — твой спасательный круг!")
    
#Обрабатываем ввод размеров обхвата груди(Продумать ограничения бы).
@dp.message(StateFilter(FSMform.chest), control)
async def chest_done(message:Message, state: FSMContext):
    await state.update_data(chest=int(message.text))
    await message.answer("🎀 А теперь талия! Введи обхват в см (только честно!)\n\n"
                         "➤ Пример: *72*. Я не сужу, я помогаю 😉\n\n"
                         "⚠️ Если что-то пошло не так — /cancel спасет!")
    await state.set_state(FSMform.waist)

@dp.message(StateFilter(FSMform.chest))
async def chest_error(ms: Message):
    await ms.answer("❌ Кажется, что-то не то! Попробуй еще раз!\n\n"
"➤ Пример: *85*. И помни: /cancel — твой спасательный круг!")
    
@dp.message(StateFilter(FSMform.waist), control)
async def waist_done(ms: Message, state: FSMContext):
    await state.update_data(waist=int(ms.text))
    await ms.answer("🍑 Время для секретных данных! Обхват *одного* бедра в см?\n\n"
                    "➤ Например: *65*. Никто не увидит, кроме меня!\n\n"
                    "⚠️ Хочешь переделать? Жми /cancel!")
    await state.set_state(FSMform.hips)


@dp.message(StateFilter(FSMform.waist))
async def waist_error(ms: Message):
    await ms.answer("❌ Кажется, что-то не то! Попробуй еще раз!\n\n"
"➤ Пример: *85*. И помни: /cancel — твой спасательный круг!")
    
@dp.message(StateFilter(FSMform.hips),control)
async def hips_done(ms: Message, state: FSMContext):
    await state.update_data(hips=int(ms.text))
    await ms.answer("🏋️ Теперь плечи! Измерь расстояние между косточками (в см).\n\n"
                    "➤ Совет: можно использовать рубашку для точности 👕\n\n"
                    "⚠️ Устал? /cancel — и мы прервёмся")
    await state.set_state(FSMform.shoulder_width)

@dp.message(StateFilter(FSMform.hips))
async def hips_error(ms: Message):
    await ms.answer("❌ Кажется, что-то не то! Попробуй еще раз!\n\n"
"➤ Пример: *85*. И помни: /cancel — твой спасательный круг!")

@dp.message(StateFilter(FSMform.shoulder_width), control)
async def sw_done(ms: Message, state: FSMContext):
    await state.update_data(shoulder_width=int(ms.text))
    await ms.answer("🧣 Обхват шеи! Да-да, это важно для идеальной рубашки!\n\n"
                    "➤ Пример: *38*.\n\n"
                    "⚠️ Если надоело — /cancel всегда поможет!")
    await state.set_state(FSMform.neck)

@dp.message(StateFilter(FSMform.shoulder_width))
async def sw_error(ms: Message):
    await ms.answer("❌ Кажется, что-то не то! Попробуй еще раз!\n\n"
"➤ Пример: *85*. И помни: /cancel — твой спасательный круг!")
    

@dp.message(StateFilter(FSMform.neck), control)
async def neck_done(ms:Message, state: FSMContext):
    await state.update_data(neck=int(ms.text))
    await ms.answer("⚖️ Сколько весишь? Только честно (я не расскажу никому)!\n\n"
                    "➤ Например: *200*.\n\n"
                    "⚠️ Если ошибся — жми /cancel!")
    await state.set_state(FSMform.massa)

@dp.message(StateFilter(FSMform.neck))
async def neck_error(ms:Message):
     await ms.answer("❌ Кажется, что-то не то! Попробуй еще раз!\n\n"
"➤ Пример: *85*. И помни: /cancel — твой спасательный круг!")
     
@dp.message(StateFilter(FSMform.massa),control)
async def massa_done(ms:Message, state: FSMContext):
    await state.update_data(massa=float(ms.text))
    await ms.answer("🦾 Финальный рывок! Длина руки от плеча до запястья (в см).\n\n"
                    "➤ Пример: *58*. Ты почти у цели! 🚀\n\n"
                    "⚠️ Если что-то не так — /cancel исправит всё!")
    await state.set_state(FSMform.len_arm)

@dp.message(StateFilter(FSMform.massa))
async def massa_error(ms:Message):
     await ms.answer("❌ Кажется, что-то не то! Попробуй еще раз!\n\n"
"➤ Пример: *85*. И помни: /cancel — твой спасательный круг!")
     
@dp.message(StateFilter(FSMform.len_arm), control)
async def len_arm_done(ms:Message, state: FSMContext):
    await state.update_data(len_arm=float(ms.text))
    
    db = get_db()
    data = await state.get_data()
    if data.get('gender') == 'male':
        await ms.answer("Поздравляю, вы заполнили параметры, теперь можно создавать 3д модель!!!!\n\n" \
    "Свои размеры вы можете увидеть, нажав на кнопку:\n<Мои размеры>")
        person = db.query(Person).filter(Person.id==ms.from_user.id).first()
        person.gender = data.get('gender')
        person.chest = data.get('chest')
        person.waist = data.get('waist')
        person.hips = data.get('hips')
        person.shoulder_width = data.get('shoulder_width')
        person.height = data.get('height')
        person.neck = data.get('neck')
        person.massa = data.get('massa')
        person.len_arm = data.get('len_arm')
        db.commit()
        db.close()
        await state.clear()
    else:
        await ms.answer("Отлично!!! Осталось ввести последний параметр. \n Введите размер груди(я никому не расскажу).")
        await state.set_state(FSMform.chest_girl)

  
@dp.message(StateFilter(FSMform.len_arm))
async def massa_error(ms:Message):
    await ms.answer("❌ Кажется, что-то не то! Попробуй еще раз!\n"
"➤ Пример: *85*. И помни: /cancel — твой спасательный круг!")
    
@dp.message(StateFilter(FSMform.chest_girl), control)
async def chest_girl(ms:Message, state:FSMContext):
    await state.update_data(chest_girl=int(ms.text))
    await ms.answer("Поздравляю, вы заполнили параметры, теперь можно создавать 3д модель!!!!\n\n" \
    "Свои размеры вы можете увидеть, нажав на кнопку:\n<Мои размеры>")
    db = get_db()
    data = await state.get_data()
    person = db.query(Person).filter(Person.id==ms.from_user.id).first()
    person.gender = data.get('gender')
    person.chest = data.get('chest')
    person.waist = data.get('waist')
    person.hips = data.get('hips')
    person.shoulder_width = data.get('shoulder_width')
    person.height = data.get('height')
    person.neck = data.get('neck')
    person.massa = data.get('massa')
    person.len_arm = data.get('len_arm')
    person.chest_girl = data.get('chest_girl')
    db.commit()
    db.close()
    await state.clear()


@dp.message(F.text=="Мои размеры", StateFilter(default_state))
async def size_person(ms:Message):
    db = get_db()
    person = db.get(Person, ms.from_user.id)
    if person.gender == 'female':
        await ms.answer(
            f'Пол: Женский\n'
            f'Обхват груди: {person.chest} см\n'
            f'Талия: {person.waist} см\n'
            f'Бёдра: {person.hips} см\n'
            f'Ширина плечь: {person.shoulder_width} см\n'
            f'Рост: {person.height} см\n'
            f'Размер груди: {person.chest_girl}\n'
            f'Шея: {person.neck} см\n'
            f'Масса: {person.massa} кг\n'
            f'Длинна рук: {person.len_arm} см'
            )
    else:
        await ms.answer(
            f'Пол: Мужской\n'
            f'Обхват груди: {person.chest} см\n'
            f'Талия: {person.waist} см\n'
            f'Бёдра: {person.hips} см\n'
            f'Ширина плечь: {person.shoulder_width} см\n'
            f'Рост: {person.height} см\n'
            f'Шея: {person.neck} см\n'
            f'Масса: {person.massa} кг\n'
            f'Длинна рук: {person.len_arm} см'
            )
    db.close()


#Основная функция вот тут будет всё происходить с блендером...
@dp.message(F.photo, StateFilter(default_state))
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



BLENDER_EXECUTABLE = r'C:\Program Files\Blender 4.4\blender.exe'  # Путь к Blender
BLENDER_SCRIPT = 'blender2_script.py'  # Путь к вашему скрипту
RENDER_OUTPUT_DIR = 'renders'  # Директория для временных файлов


async def run_blender_async(output_path: str) -> bool:
    """Асинхронно запускает Blender с указанным скриптом"""
    command = [
        BLENDER_EXECUTABLE,
        '--background',
        '--python', BLENDER_SCRIPT,
        '--',  # Разделитель для аргументов скрипта
        output_path
    ]
    
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    await process.communicate()
    return process.returncode == 0


def is_file_available(filepath: str) -> bool:
    try:
        with open(filepath, 'rb'):
            return True
    except IOError:
        return False


@dp.message(F.text=="Примерить одежду", StateFilter(default_state))
async def answer(message:Message):
    """Обработчик команды запуска рендеринга"""
    # Создаем уникальное имя файла
    os.makedirs(RENDER_OUTPUT_DIR, exist_ok=True)
    filename = f"{message.from_user.id}.mp4"
    output_dir = 'D:\\project\\VirtuFit\\video'
    output_path = os.path.join(output_dir, filename)
    
    await message.reply("🚀 Начинаю рендеринг...")
    
    try:
        success = await run_blender_async(output_path)
        if not success:
            raise Exception("Ошибка в процессе рендеринга")
        

        for _ in range(10):
            if os.path.exists(output_path) and is_file_available(output_path):
                break
            await asyncio.sleep(1)
        else:
            raise Exception("Файл не освободился после рендеринга")
        

        if os.path.exists(output_path):
            video = FSInputFile(output_path)
            await bot.send_video(
                chat_id=message.chat.id, 
                video=video
                                 )
            os.remove(output_path)
        else:
            await message.reply("❌ Файл не был создан")
            
    except Exception as e:
        await message.reply(f"⚠️ Ошибка: {str(e)}")
        if os.path.exists(output_path):
            os.remove(output_path)


@dp.message(F.text == "💰Подписка💰", StateFilter(default_state))
async def pay(message: Message):
    await message.answer("Выбери режим!", reply_markup=kb_builder_payments.as_markup(resize_keyboard=True, one_time_keyboard=True))

@dp.message(F.text == "🙂Пользователь🙂", StateFilter(default_state))
async def b2c(message: Message):
    await message.answer("Тут что нибудь появится! Скоро...")

@dp.message(F.text == "💼Бизнес💼", StateFilter(default_state))
async def b2b(message: Message):
    await message.answer("Тут что нибудь появится! Скоро...")


@dp.message(F.text == "Что умеешь?", StateFilter(default_state))
async def info(ms:Message):
    await ms.answer("Привет! Я бот VirtualFit.\n\nЯ могу помочь тебе примерить одежду.\nСначала введи свои размеры, потом сможешь отправить мне фотографию той одежды, которую хочешь примерить, а я пришлю тебе видео на которой модель с твоими размерами в этой одежде!")

@dp.message(F.text == "Футболка", StateFilter(default_state))
async def t_short(message: Message):
    db = get_db()
    person =  db.get(Person, message.from_user.id)
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
    await message.answer("Я такое не умею((")



if __name__=='__main__':
    dp.run_polling(bot)


