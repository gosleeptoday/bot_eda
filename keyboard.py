from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import datetime

reg = ReplyKeyboardMarkup(resize_keyboard=True)
reg.add(KeyboardButton(text="Зарегистрироваться", request_contact=True))

ParentsButton = ReplyKeyboardMarkup(resize_keyboard=True)
ParentsButton.add("Запись на обед").add("Информация о ребенке").add("Помощь")


async def generate_dates():
    weeks = InlineKeyboardMarkup()
    today = datetime.date.today()
    if today.weekday() == 3: #проверка на четверг, что бы генерировалось пт и пн
        next_friday = today + datetime.timedelta(days=(4 - today.weekday()))
        next_monday = today + datetime.timedelta(days=(7 - today.weekday()))
        weeks.add(
                InlineKeyboardButton(text=next_friday.strftime("%d-%m-%Y"), callback_data=next_friday.strftime("%d-%m-%Y"))
            ).add(
                InlineKeyboardButton(text=next_monday.strftime("%d-%m-%Y"), callback_data=next_monday.strftime("%d-%m-%Y"))
            )
    elif today.weekday() >= 4: #в пятницу и выходные генерируется даты пн и вторника
        next_monday = today + datetime.timedelta(days=(7 - today.weekday() + 1))
        next_tuesday = next_monday + datetime.timedelta(days=1)
        weeks.add(
                InlineKeyboardButton(text=next_monday.strftime("%d-%m-%Y"), callback_data=next_monday.strftime("%d-%m-%Y"))
            ).add(
                InlineKeyboardButton(text=next_tuesday.strftime("%d-%m-%Y"), callback_data=next_tuesday.strftime("%d-%m-%Y"))
            ).add(
                InlineKeyboardButton(text="Закончить", callback_data="cancel")
            )
    else:
        next_day = today + datetime.timedelta(days=1)
        day_after_next = today + datetime.timedelta(days=2)
        weeks.add(
                InlineKeyboardButton(text=next_day.strftime("%d-%m-%Y"), callback_data=next_day.strftime("%d-%m-%Y"))
            ).add(
                InlineKeyboardButton(text=day_after_next.strftime("%d-%m-%Y"), callback_data=day_after_next.strftime("%d-%m-%Y"))
            ).add(
                InlineKeyboardButton(text="Закончить", callback_data="cancel")
            )
    return weeks

get_kids =InlineKeyboardMarkup()
get_kids.add(
        InlineKeyboardButton(text="Ввести дату вручную", callback_data="hand_date")
    ).add(
        InlineKeyboardButton(text="Показать ближайшие даты", callback_data="close_date")
    ).add(
        InlineKeyboardButton(text="Выйти", callback_data= "cancel")
    )

adm_menu = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
adm_menu.add("Рассылка").add("Показать кто записался").add("Выйти")


