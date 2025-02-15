from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

# Состояние пользователя при создании тренировки
class CreatWorkout(StatesGroup):
    date = State()
    title = State()
    exercise = State()

# Состояние пользователя при просмотре тренировок
class ChechWorkout(StatesGroup):
    id_delete = State()
    date = State()

# Состояние пользователя при создании замера
class CreatBody(StatesGroup):
    date = State()
    chest = State()
    waist = State()
    hips = State()
    legs = State()
    arms = State()

# Состояние пользователя при просмотре замеров
class ChechBody(StatesGroup):
    id_delete = State()

# Коллекция хранящее упражнения при создании тренировки {telegram_id: ex}
TimeUserTren = {}