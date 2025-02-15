import time
import asyncio
from gc import callbacks
from pkgutil import get_data
from time import sleep

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import date, datetime

from UserState import *
import keyboard as kb
import database.requests as rq
from pyexpat.errors import messages

router = Router()

# Вызывается при запуске бота
@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_User(message.from_user.id)
    await message.answer("Здравствуй, этот бот поможет тебе в создании тренировочного плана и отслеживания прогресса тренировок"
                         , reply_markup=kb.Menu)

@router.callback_query(F.data == "to_main")
async def Menu(callback: CallbackQuery):
    await callback.message.edit_text("Выберите одно из действий", reply_markup=kb.Menu)

# Вызывается при нажатии на кнопку "Просмотреть, cоздать или изменить тренировку"
@router.callback_query(F.data == "Doworkouts")
async def CreatOrChangeWorkout(callback: CallbackQuery):
    await callback.message.edit_text("Вы хотите просмотреть или создать тренировку?", reply_markup=kb.Creat_or_Check)
# -----------------------------------Просмотр тренировок----------------------------------------------
@router.callback_query(F.data == "Check_workout")
async def WatchWorkout_One(callback: CallbackQuery):
    today = date.today()
    await callback.message.edit_text(f"Ваши тренировки за {today.month}.{today.year} ", reply_markup=await kb.do_workout(callback.from_user.id, today))

@router.callback_query(F.data.startswith("workout_"))
async def WatchWorkout_Two(callback: CallbackQuery, state:FSMContext):
    date = callback.data.split("_")[1]
    name = callback.data.split("_")[2]
    training = await rq.get_SpecTraining(callback.from_user.id, date, name)
    await callback.message.answer(f"Ваша тренировка '{training.name}' от {training.date} \nВ которой следующие упражнения:")
    for ex in range(len(training.description.split("+"))):
        await callback.message.answer(f"{ex+1}. {training.description.split("+")[ex]}")
        await asyncio.sleep(0.2)
    await state.update_data(id_delete=training.id)
    await callback.message.answer("Выберите действие", reply_markup=kb.ChangeOrDel_Training)

# -----------------------------------Удаление тренировок----------------------------------------------
@router.callback_query(F.data == "Del_workout")
async def DelWorkout(callback: CallbackQuery, state:FSMContext):
    id = await state.get_data()
    await rq.set_DelTraining(id["id_delete"])
    await callback.message.edit_text("Тренировка удалена, выберите действие", reply_markup=kb.Menu)
    await state.clear()
# ----------------------------------------------------------------------------------------------------
# -----------------------------------Смена даты тренировок--------------------------------------------
@router.callback_query(F.data == "Change_date")
async def ChangeDateWorkout_One(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChechWorkout.date)
    await callback.message.answer("Введите месяц за который хотите просмотреть тренировку в формате '01.2000' (месяц.год)", reply_markup=kb.Finish_Typing)

@router.message(ChechWorkout.date)
async def ChangeDateWorkout_Two(message: Message, state: FSMContext):
    try:
        if message.text == "Закончить ввод":
            await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Выберите действие", reply_markup=kb.Finish_Typing)
        else:
            date = datetime.strptime("01." + message.text, '%d.%m.%Y').date()
            await message.answer(f"Ваши тренировки за {message.text}", reply_markup=await kb.do_workout(message.from_user.id, date))
            await state.clear()
    except:
        await message.answer("Введите корректную дату в формате '01.2000'")
# ----------------------------------------------------------------------------------------------------
# -----------------------------Поэтапное добавление тренировки----------------------------------------
@router.callback_query(F.data == "Creat_workout")
async def CreatWorkout_One(callback: CallbackQuery, state:FSMContext):
    await state.set_state(CreatWorkout.date)
    await callback.message.answer("Введите дату тренировки в формате '01.01.2000'", reply_markup=kb.Finish_Typing)

@router.message(CreatWorkout.date)
async def CreatWorkout_Two(message: Message, state: FSMContext):
    try:
        if message.text == "Закончить ввод":
            await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Выберите одно из действий", reply_markup=kb.Menu)
            await state.clear()
        else:
            date_time_obj = datetime.strptime(message.text, '%d.%m.%Y').date()
            await state.update_data(date=message.text)
            await state.set_state(CreatWorkout.title)
            await message.answer("Введите название тренировки")
    except:
        await message.answer("Введите корректную дату в формате '01.01.2000'")

@router.message(CreatWorkout.title)
async def CreatWorkout_Three(message: Message, state: FSMContext):
    if message.text == "Закончить ввод":
        await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Выберите действие", reply_markup=kb.Menu)
        await state.clear()
    else:
        await state.update_data(title = message.text)
        await state.set_state(CreatWorkout.exercise)
        data = await state.get_data()
        await message.answer("Вводите упражнение, для окончания ввода нажмите 'Закончить ввод'", reply_markup=kb.Finish_Typing)

@router.message(CreatWorkout.exercise)
async def CreatWorkout_Four(message: Message, state: FSMContext):
    if message.text == "Закончить ввод":
        if message.from_user.id in TimeUserTren:
            await state.update_data(exercise=message.text)
            data = await state.get_data()

            await rq.set_Workout(message.from_user.id, data, TimeUserTren)

            del TimeUserTren[message.from_user.id]
            await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Тренировка сохранена", reply_markup=kb.Menu)
            await state.clear()
        else:
            await message.answer("Ввод завершен, тренировка не сохранена в связи с отсутствием упражнений", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Выберите действие", reply_markup=kb.Menu)
            await state.clear()
    elif message.from_user.id not in TimeUserTren:
        TimeUserTren[message.from_user.id] = message.text
    else:
        TimeUserTren[message.from_user.id] += "+" + message.text
# ----------------------------------------------------------------------------------------------------

@router.callback_query(F.data == "Dobody")
async def CreatOrChangeBody(callback: CallbackQuery):
    await callback.message.edit_text("Вы хотите просмотреть или записать замеры?", reply_markup=kb.Write_or_Check)

# -----------------------------Поэтапное добавление замеров----------------------------------------
@router.callback_query(F.data == "Creat_body")
async def CreatBody_One(callback: CallbackQuery, state:FSMContext):
    await state.set_state(CreatBody.date)
    await callback.message.answer("Введите дату замеров в формате '01.01.2000'", reply_markup=kb.Finish_Typing)

@router.message(CreatBody.date)
async def CreatBody_Two(message: Message, state: FSMContext):
    try:
        if message.text == "Закончить ввод":
            await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Выберите одно из действий", reply_markup=kb.Menu)
            await state.clear()
        else:
            date_time_obj = datetime.strptime(message.text, '%d.%m.%Y').date()
            await state.update_data(date=message.text)
            await state.set_state(CreatBody.chest)
            await message.answer("Введите обхват груди")
    except:
        await message.answer("Введите корректную дату в формате '01.01.2000'")

@router.message(CreatBody.chest)
async def CreatBody_Three(message: Message, state: FSMContext):
    if message.text == "Закончить ввод":
        await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Выберите одно из действий", reply_markup=kb.Menu)
        await state.clear()
    else:
        await state.update_data(chest = message.text)
        await state.set_state(CreatBody.waist)
        await message.answer("Введите обхват талии")

@router.message(CreatBody.waist)
async def CreatBody_Four(message: Message, state: FSMContext):
    if message.text == "Закончить ввод":
        await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Выберите одно из действий", reply_markup=kb.Menu)
        await state.clear()
    else:
        await state.update_data(waist = message.text)
        await state.set_state(CreatBody.hips)
        await message.answer("Введите обхват бедер")

@router.message(CreatBody.hips)
async def CreatBody_Five(message: Message, state: FSMContext):
    if message.text == "Закончить ввод":
        await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Выберите одно из действий", reply_markup=kb.Menu)
        await state.clear()
    else:
        await state.update_data(hips = message.text)
        await state.set_state(CreatBody.legs)
        await message.answer("Введите обхват ног")

@router.message(CreatBody.legs)
async def CreatBody_Six(message: Message, state: FSMContext):
    if message.text == "Закончить ввод":
        await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Выберите одно из действий", reply_markup=kb.Menu)
        await state.clear()
    else:
        await state.update_data(legs = message.text)
        await state.set_state(CreatBody.arms)
        await message.answer("Введите обхват рук")

@router.message(CreatBody.arms)
async def CreatBody_Seven(message: Message, state: FSMContext):
    if message.text == "Закончить ввод":
        await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Выберите одно из действий", reply_markup=kb.Menu)
        await state.clear()
    else:
        await state.update_data(arms = message.text)
        await state.set_state(CreatBody.arms)

        data = await state.get_data()

        await rq.set_Body(message.from_user.id, data)
        await message.answer("Ввод завершен", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Замеры сохранены", reply_markup=kb.Menu)
        await state.clear()

# ----------------------------------------------------------------------------------------------------
# -----------------------------------Просмотр замеров----------------------------------------------
@router.callback_query(F.data == "Check_body")
async def WatchBody_One(callback: CallbackQuery):
    await callback.message.edit_text(f"Ваши замеры", reply_markup=await kb.do_body(callback.from_user.id))

@router.callback_query(F.data.startswith("body_"))
async def WatchBody_Two(callback: CallbackQuery, state:FSMContext):
    date = callback.data.split("_")[1]
    measuring = await rq.get_SpecBody(callback.from_user.id, date)
    await callback.message.edit_text(f"Ваши замеры от {measuring.date}:\nОбхват груди: {measuring.chest} \nОбхват талии: {measuring.chest} \nОбхват бедер: {measuring.chest} \n"
                                  f"Обхват ног: {measuring.chest} \nОбхват рук: {measuring.chest}", reply_markup=kb.ChangeOrDel_Body)

    await state.update_data(id_delete=measuring.id)
# ----------------------------------------------------------------------------------------------------
# -------------------------------------Удаление замеров-----------------------------------------------
@router.callback_query(F.data == "Del_body")
async def DelBody_One(callback: CallbackQuery, state:FSMContext):
    id = await state.get_data()
    await rq.set_DelBody(id["id_delete"])
    await callback.message.edit_text("Замеры удалены", reply_markup=kb.Menu)

    await state.clear()
# ----------------------------------------------------------------------------------------------------

