зшimport os
import asyncio
import logging

from dotenv import load_dotenv

from UserState import *
from aiogram import Bot, Dispatcher
from Handlers import router
from database.models import async_main

load_dotenv()
bot = Bot(token = os.getenv("TOKEN"))
dp = Dispatcher()

async def main():
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    #logging.basicConfig(level=logging.INFO) Инфа по действиям в боте
    try:
        asyncio.run((main()))
    except KeyboardInterrupt:
        print("Exit")
