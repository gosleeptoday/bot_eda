import aiogram
from aiogram import Bot, Dispatcher
from aiogram.types import Message 
import config
import datetime
import keyboard
from db import child, parents, reg, schedule
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(token = config.token)
db = config.maindb
dp = Dispatcher(bot=bot, storage=storage)

class states(StatesGroup):
    hand_date = State()
    close_date = State()
    send = State()
    schedsend = State()
    zapis = State()

@dp.message_handler(commands=['adm'])
async def admin(message: Message):
    if message.from_user.id in config.admins:
        await bot.send_message(message.from_user.id, "Админ меню", reply_markup=keyboard.adm_menu)

@dp.message_handler(commands=['start'])
async def first_start(message: Message):
    if reg.select().where(reg.tgid == message.from_user.id).exists():
        await bot.send_message(message.from_user.id, "Вы уже зарегестрированы. Для управления ботом используйте кнопки ниже.", reply_markup=keyboard.ParentsButton)
    else:
        await bot.send_message(message.from_user.id, "Здраствуйте! Для начала использования бота требуется регистрация по номеру телефона. Для этого нажмите кнопку ниже.", reply_markup=keyboard.reg)

@dp.message_handler(content_types=['contact'])
async def regestr(message: Message):
    if parents.select().where(parents.number == message.contact.phone_number.replace('+', '')).exists() and not reg.select().where(reg.par_id == parents.select(parents.id).where(parents.number == message.contact.phone_number.replace('+', ''))).exists():
        print(f"Регаю нового пользователя c номером {message.contact.phone_number}")
        info = parents.get(parents.number == message.contact.phone_number.replace('+', ''))
        reg.create(par_id=info.id, child_id=info.child_id, tgid = message.from_user.id)
        await bot.send_message(message.from_user.id, f"Регистрация прошла успешно! Ваш ребенок {child.get(id = info.child_id).fio}", reply_markup=keyboard.ParentsButton)
    elif reg.select().where(reg.par_id == parents.select(parents.id).where(parents.number == message.contact.phone_number.replace('+', ''))).exists(): 
        await bot.send_message(message.from_user.id, "Не треуется проходить повторную регистрацию. Вы уже зарегистрированы. Используйте кнопки для управления ботом.", reply_markup=keyboard.ParentsButton)
    else:
        await bot.send_message(message.from_user.id, "Доступ ограничен, так как ваш номер не найден в базе данных.")
        print(f"{message.contact.phone_number.replace('+', '')} пытался получить доступ к боту. Номер не найден в бд, доступ ограничен.")

@dp.message_handler(content_types=['text'], state= None)
async def commands(message: Message):
    if message.text == "Запись на обед":
        board = await keyboard.generate_dates()
        await bot.send_message(message.from_user.id, "Выберите дату для записи ребёнка на обед.", reply_markup=board)
        await states.zapis.set()
    elif message.text == "Информация о ребенке":
        children = child.get(child.id == reg.get(reg.tgid == message.from_user.id).child_id)
        sch_month = schedule.select().where(schedule.child_id == children.id)
        if regs_list := [_.day for _ in sch_month]:
            resault = "Список дат на которые вы записаны в этом месяце:\n" + "\n".join(regs_list)
        else:
            resault = "В этом месяце вы не записаны "
        await bot.send_message(message.from_user.id, f"ФИО вашего ребенка: {children.fio}\n\n{resault}")
    elif message.text == "Помощь":
        await bot.send_message(message.from_user.id, "Данный бот предназначен для записи детей на обеды.\nЕсли возникла какая-то техническая ошибка, бот не работает или не отвечает, а так же по рекламным предложениям или для покупки бота пишите в тг @printmyname")
    elif message.text == "Рассылка" and message.from_user.id in config.admins:
        await bot.send_message(message.from_user.id, "Введите текст рассылки:", reply_markup=keyboard.adm_menu)
        await states.send.set()
    elif message.text == "Показать кто записался" and message.from_user.id in config.admins:
        await bot.send_message(message.from_user.id, "Выберите день недели", reply_markup=keyboard.get_kids)
        await states.schedsend.set()
    else:
        await bot.send_message(message.from_user.id, "Неизвестная команда", reply_markup=keyboard.ParentsButton)

@dp.message_handler(state=states.send)
async def sendtoall(message: Message, state: FSMContext):
    success = 0
    error = 0
    for i in reg.select():
        try:
            success += 1
            await bot.send_message(i.tgid, message.text, parse_mode="html")
        except Exception:
            error += 1
    await bot.send_message(message.from_user.id, f"Рассылка окончена!\n\n✅Успешно: {success}\n❌Ошибок: {error}")
    await state.finish()

@dp.callback_query_handler(lambda call: True, state=states.zapis)
async def answer(call, state: FSMContext): 
    child = parents.select().where(parents.id == reg.get(reg.tgid == call.from_user.id).par_id).get()
    day = [_.day for _ in schedule.select().where(schedule.child_id == reg.get(reg.tgid == call.from_user.id).child_id)]
    if call.data == "cancel":
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, "Вернулся в меню, используйте его для дальнейшего управления ботом", reply_markup=keyboard.ParentsButton)
        await state.finish()
    elif call.data not in day:
        schedule.create(child_id = child.child_id, day = call.data) 
        await bot.send_message(call.from_user.id, "Записал на выбранный день.")
    else:
        await bot.send_message(call.from_user.id, "Вы уже записаны на этот день в текущей неделе.")

@dp.callback_query_handler(lambda call: True, state=states.schedsend)
async def givekids(call, state: FSMContext):
    if call.data == "cancel":
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, "Вернулся в меню, используйте его для дальнейшего управления ботом", reply_markup=keyboard.adm_menu)
        await state.finish()
    elif call.data == "hand_date":
        await bot.send_message(call.from_user.id, "Введите дату, за которую вы хотите получить список детей. ОБЯЗАТЕЛЬНО вводите дату в формате ДД-ММ-ГГГГ\n\nПример: 13-09-2005")
        await state.set_state(states.hand_date)
    else:
        board = await keyboard.generate_dates()
        await bot.send_message(call.from_user.id, "Выберите дату из приведенных ниже", reply_markup=board)
        await state.set_state(states.close_date)

@dp.message_handler(state=states.hand_date)
async def handdatekids(message: Message, state: FSMContext):
    fio_list = []
    try:
        res_1 = schedule.select().where(schedule.day == message.text)
        for schedule_entry in res_1:
            if child_entry := child.get(child.id == schedule_entry.child_id):
                fio_list.append(child_entry.fio)
    except Exception as e :
        print(e)
    if fio_list!=[]:
        message_text = "Список детей:\n" + "\n".join(fio_list)
        await bot.send_message(message.from_user.id, message_text)
    else:
        await bot.send_message(message.from_user.id, "Либо вы ввели неправильную дату, либо произошла ошибка. Перепроверьте введенную вами дату и попробуйте повторить операцию.")
    await state.finish()

@dp.callback_query_handler(lambda call: True, state=states.close_date)
async def closedatekids(call, state: FSMContext):
    if call.data == "cancel":
        await state.finish()
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, "Вернулся в меню, используйте его для дальнейшего управления ботом", reply_markup=keyboard.adm_menu)
        
    fio_list = []
    try:
        res_1 = schedule.select().where(schedule.day == call.data)
        for schedule_entry in res_1:
            if child_entry := child.get(child.id == schedule_entry.child_id):
                fio_list.append(child_entry.fio)
    except Exception as e :
        print(e)
    if fio_list!=[]:
        message_text = "Список детей:\n" + "\n".join(fio_list)
        await bot.send_message(call.from_user.id, message_text)
    await state.finish()

if __name__ == '__main__':
    aiogram.executor.start_polling(dp)