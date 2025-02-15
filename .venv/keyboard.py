from gc import callbacks

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardButton, CallbackData, InlineKeyboardBuilder

from database.models import Workout
import database.requests as rq

Menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Просмотреть или создать тренировку 💪", callback_data="Doworkouts")],
    [InlineKeyboardButton(text="Просмотреть или записать замеры 📒", callback_data="Dobody")]
], resize_keyboard=True)

Write_or_Check = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Просмотреть замеры 👀", callback_data="Check_body")],
    [InlineKeyboardButton(text="Записать замеры ✏️️", callback_data="Creat_body")],
    [InlineKeyboardButton(text="Вернуться в меню 🔙", callback_data="to_main")]
], resize_keyboard=True)

Creat_or_Check = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Просмотреть тренировки 👀", callback_data="Check_workout")],
    [InlineKeyboardButton(text="Создать тренировку 🔨", callback_data="Creat_workout")],
    [InlineKeyboardButton(text="Вернуться в меню 🔙", callback_data="to_main")]
], resize_keyboard=True)

Finish_Typing = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Закончить ввод")]
], resize_keyboard=True)

ChangeOrDel_Training = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Удалить тренировку ❌", callback_data="Del_workout")],
    [InlineKeyboardButton(text="Вернуться в меню 🔙", callback_data="to_main")]
], resize_keyboard=True)

ChangeOrDel_Body = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Удалить замеры ❌", callback_data="Del_body")],
    [InlineKeyboardButton(text="Вернуться в меню 🔙", callback_data="to_main")]
], resize_keyboard=True)

async def do_workout(user_id, today):
    workouts = await rq.get_AllWorkout(user_id)
    keyboard = InlineKeyboardBuilder()
    for workout in workouts:
        if workout.date.year == today.year and workout.date.month == today.month:
            keyboard.add(InlineKeyboardButton(text=f"{workout.name} за {workout.date}", callback_data=f"workout_{workout.date}_{workout.name}"))
    keyboard.add(InlineKeyboardButton(text="Сменить дату", callback_data="Change_date"))
    keyboard.add(InlineKeyboardButton(text="На главную", callback_data="to_main"))
    return keyboard.adjust(2).as_markup()

async def do_body(user_id):
    bodys = await rq.get_AllBody(user_id)
    keyboard = InlineKeyboardBuilder()
    for body in bodys:
        keyboard.add(InlineKeyboardButton(text=f"Замеры за {body.date}", callback_data=f"body_{body.date}"))
    keyboard.add(InlineKeyboardButton(text="На главную", callback_data="to_main"))
    return keyboard.adjust(2).as_markup()