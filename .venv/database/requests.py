from tabnanny import check

from certifi import where
from database.models import async_session
from database.models import User, Workout, Body
from sqlalchemy import select, delete

from datetime import datetime

# Добавляет пользователя в БД
async def set_User(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

# Добавляет пользователя тренировку в БД
async def set_Workout(tg_id, data, timeusertren):
    async with async_session() as session:
        date_time_obj = datetime.strptime(data["date"], '%d.%m.%Y').date()
        session.add(Workout(user=tg_id, date=date_time_obj, name=data["title"], description=timeusertren[tg_id]))
        await session.commit()

# Возвращает все тренировки пользователя
async def get_AllWorkout(tg_id):
    async with async_session() as session:
        return await session.scalars(select(Workout).where(Workout.user == tg_id))

# Возвращает конкретную тренировку пользователя по дате и названию тренировки
async def get_SpecTraining(tg_id, date, name):
    async with async_session() as session:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        return await session.scalar(select(Workout).where(Workout.user == tg_id, Workout.date == date, Workout.name == name))

# Удаляет тренировку по ID
async def set_DelTraining(elem_id):
    async with async_session() as session:
        await session.execute(delete(Workout).where(Workout.id == elem_id))
        await session.commit()

# Добавляет замеры пользователя
async def set_Body(tg_id, data):
    async with async_session() as session:
        date_time_obj = datetime.strptime(data["date"], '%d.%m.%Y').date()
        session.add(Body(user=tg_id, date=date_time_obj, chest=data["chest"], waist=data["waist"], hips=data["hips"], legs=data["legs"], arms=data["arms"]))
        await session.commit()

# Возвращает все замеры пользователя
async def get_AllBody(tg_id):
    async with async_session() as session:
        return await session.scalars(select(Body).where(Body.user == tg_id))

# Возвращает конкретные замеры пользователя по дате
async def get_SpecBody(tg_id, date):
    async with async_session() as session:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        return await session.scalar(select(Body).where(Body.user == tg_id, Body.date == date))

# Удаляет замеры по ID
async def set_DelBody(elem_id):
    async with async_session() as session:
        await session.execute(delete(Body).where(Body.id == elem_id))
        await session.commit()
