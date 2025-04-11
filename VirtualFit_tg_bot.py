from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state,State,StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message, KeyboardButton, BotCommand, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv 
from sqlalchemy.orm import Session
from database import *
import os

def control_values(message: Message):
    return int(message.text)>0 and message.text.isdigit() and message.text not in '.,'

Base.metadata.create_all(bind=engine)

def get_db():
    db:Session = SessionLocal()
    return db

storage = MemoryStorage()



load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

#Создём кнопки
kb_builder1 = ReplyKeyboardBuilder()
kb_builder_menu = ReplyKeyboardBuilder()
buttons_1 = [KeyboardButton(text="Футболка"), KeyboardButton(text="Кофта")]
buttons_menu = [KeyboardButton(text="Подписка"), 
                KeyboardButton(text="Ввести размеры"), 
                KeyboardButton(text="Что умеешь?"), 
                KeyboardButton(text="Примерить одежду"),
                KeyboardButton(text="Реферальная программа"),
                KeyboardButton(text="Сотрудничество"),
                KeyboardButton(text="Мои размеры")
                ]
kb_builder1.row(*buttons_1, width=2)
kb_builder_menu.row(*buttons_menu, width=3)

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



kb_builder = ReplyKeyboardBuilder()

button = [KeyboardButton(text="Футболка"), KeyboardButton(text="Кофта")]

kb_builder.row(*button, width=2)


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
        text="Укажите ваш пол", 
        reply_markup=markup)
    await state.set_state(FSMform.gender)

@dp.callback_query(StateFilter(FSMform.gender), F.data.in_(['male', 'female']))
async def gender_done(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)

    await callback.message.delete()
    await callback.message.answer("Спасибо!!\nТеперь введите пожалуйста размер обхвата груди в САНТИМЕТРАХ (см).")
    await state.set_state(FSMform.chest)

@dp.message(StateFilter(FSMform.gender))
async def gender_error(message: Message):
    await message.answer("Пожалуйста, пользуйтесь кнопками, при выборе пола.\n\nЕсли хотите прервать заполнение размеров - отправьте команде /cancel")

#Обрабатываем ввод размеров обхвата груди(Продумать ограничения бы).
@dp.message(StateFilter(FSMform.chest), control_values)
async def chest_done(message:Message, state: FSMContext):
    await state.update_data(chest=int(message.text))
    await message.answer("Отлично!\nТеперь введите размер талии в САНТИМЕТРАХ (см)")
    await state.set_state(FSMform.waist)

@dp.message(StateFilter(FSMform.chest))
async def chest_error(ms: Message):
    await ms.answer("Введите корректные данные\n\nЕсли хотите прервать заполнение размеров - отправьте команде /cancel")

@dp.message(StateFilter(FSMform.waist), control_values)
async def waist_done(ms: Message, state: FSMContext):
    await state.update_data(waist=int(ms.text))
    await ms.answer("Отлично!\nТеперь введите размер бёдер в САНТИМЕТРАХ (см)")
    await state.set_state(FSMform.hips)


@dp.message(StateFilter(FSMform.waist))
async def waist_error(ms: Message):
    await ms.answer("Введите корректные данные\n\nЕсли хотите прервать заполнение размеров - отправьте команде /cancel")

@dp.message(StateFilter(FSMform.hips), control_values)
async def hips_done(ms: Message, state: FSMContext):
    await state.update_data(hips=int(ms.text))
    await ms.answer("Отлично!\nТеперь введите ширину плечь в САНТИМЕТРАХ (см)")
    await state.set_state(FSMform.shoulder_width)

@dp.message(StateFilter(FSMform.hips))
async def hips_error(ms: Message):
    await ms.answer("Введите корректные данные\n\nЕсли хотите прервать заполнение размеров - отправьте команде /cancel")


@dp.message(StateFilter(FSMform.shoulder_width), control_values)
async def sw_done(ms: Message, state: FSMContext):
    await state.update_data(shoulder_width=int(ms.text))
    await ms.answer("Отлично!\nТеперь введите рост в САНТИМЕТРАХ (см)")
    await state.set_state(FSMform.height)

@dp.message(StateFilter(FSMform.shoulder_width))
async def sw_error(ms: Message):
    await ms.answer("Введите корректные данные\n\nЕсли хотите прервать заполнение размеров - отправьте команде /cancel")


@dp.message(StateFilter(FSMform.height), control_values)
async def height_done(ms:Message, state: FSMContext):
    await state.update_data(height=int(ms.text))
    await ms.answer("Отлично!\nТеперь введите размер шеи в САНТИМЕТРАХ (см)")
    await state.set_state(FSMform.neck)

@dp.message(StateFilter(FSMform.height))
async def height_error(ms:Message):
     await ms.answer("Введите корректные данные\n\nЕсли хотите прервать заполнение размеров - отправьте команде /cancel")
    
@dp.message(StateFilter(FSMform.neck), control_values)
async def neck_done(ms:Message, state: FSMContext):
    await state.update_data(neck=int(ms.text))
    await ms.answer("Отлично!\nТеперь введите вес в КИЛЛОГРАММАХ (кг)")
    await state.set_state(FSMform.massa)

@dp.message(StateFilter(FSMform.neck))
async def neck_error(ms:Message):
     await ms.answer("Введите корректные данные\n\nЕсли хотите прервать заполнение размеров - отправьте команде /cancel")
    
@dp.message(StateFilter(FSMform.massa), lambda x: 20<float(x.text)<200 and x.text.isdigit())
async def massa_done(ms:Message, state: FSMContext):
    await state.update_data(massa=float(ms.text))
    await ms.answer("Отлично!\nТеперь введите длинну рук в САНТИМЕТРАХ (см)")
    await state.set_state(FSMform.len_arm)

@dp.message(StateFilter(FSMform.massa))
async def massa_error(ms:Message):
     await ms.answer("Введите корректные данные\n\nЕсли хотите прервать заполнение размеров - отправьте команде /cancel")
 
@dp.message(StateFilter(FSMform.len_arm), lambda x: int(x.text)>20 and int(x.text)<90 and x.text.isdigit())
async def len_arm_done(ms:Message, state: FSMContext):
    await state.update_data(len_arm=float(ms.text))
    
    db = get_db()
    data = await state.get_data()
    if data.get('gender') == 'male':
        await ms.answer("Поздравляю, вы заполнили параметры, теперь можно создавать 3д модель!!!!")
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
        await ms.answer("Отлично!!! Осталось ввести последний параметр. \n Введите размер груди.")
        await state.set_state(FSMform.chest_girl)

  
@dp.message(StateFilter(FSMform.len_arm))
async def massa_error(ms:Message):
    await ms.answer("Введите корректные данные\n\nЕсли хотите прервать заполнение размеров - отправьте команде /cancel")

@dp.message(StateFilter(FSMform.chest_girl), lambda x: 1<=int(x.text)<= 5)
async def chest_girl(ms:Message, state:FSMContext):
    await state.update_data(chest_girl=int(ms.text))
    await ms.answer("Поздравляю, вы заполнили параметры, теперь можно создавать 3д модель!!!!\n\n" \
    "Свои размеры вы можете увидеть, нажав на кнопку <Мои размеры>")
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
    if person.chest_girl != None:
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

@dp.message(F.text=="Примерить одежду", StateFilter(default_state))
async def answer(ms:Message):
    await ms.answer("Хорошо, давай примерим!!!\n\nОтправь мне фото одежды, которую хотел бы примерить!")

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




# # import bpy
# import sys

# def main():
#     argv = sys.argv[sys.argv.index("--") + 1:]
#     dimensions = list(map(float, argv[0].split(',')))
#     output_path = argv[1]
    
#     # Получаем объект модели
#     obj = bpy.data.objects['Body']
    
#     # Изменяем размеры (пример для параметрической модели)
#     obj.dimensions = dimensions
    
#     # Настройка рендера
#     bpy.context.scene.render.filepath = output_path
#     bpy.ops.render.render(write_still=True)

# if __name__ == "__main__":
#     main()

# async def run_blender_script(user_id, dimensions):
#     output_path = f"renders/{user_id}_output.png"
#     blender_script = "model_adjust.py"
    
#     proc = await asyncio.create_subprocess_exec(
#         "blender", "-b", "model.blend", 
#         "-P", blender_script,
#         "--", dimensions, output_path,
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE
#     )
    
#     await proc.wait()
#     return output_path

# @dp.message_handler(regexp=r'\d+,\s*\d+,\s*\d+')
# async def process_dimensions(message: types.Message):
#     user_id = message.from_user.id
#     try:
#         await message.answer("Начинаю обработку...")
#         output = await run_blender_script(user_id, message.text)
        
#         with open(output, 'rb') as photo:
#             await message.answer_photo(photo)
        
#         os.remove(output)  # Очистка временных файлов
#     except Exception as e:
#         await message.answer(f"Ошибка: {str(e)}")