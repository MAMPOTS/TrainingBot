from sqlalchemy import BigInteger, String, ForeignKey, Date, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, async_session
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_async_engine(url=os.getenv("SQLALCHEMY_URL"))

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

class Workout(Base):
    __tablename__ = "Workouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    date = mapped_column(Date)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(50))

    user: Mapped[BigInteger] = mapped_column(ForeignKey("users.tg_id"))

class Body(Base):
    __tablename__ = "Bodys"

    id: Mapped[int] = mapped_column(primary_key=True)
    date = mapped_column(Date)
    chest: Mapped[float] = mapped_column(Float(6))
    waist: Mapped[float] = mapped_column(Float(6))
    hips: Mapped[float] = mapped_column(Float(6))
    legs: Mapped[float] = mapped_column(Float(6))
    arms: Mapped[float] = mapped_column(Float(6))

    user: Mapped[BigInteger] = mapped_column(ForeignKey("users.tg_id"))

async def async_main():
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all) Удаление всех данных в БД
        await conn.run_sync(Base.metadata.create_all)





