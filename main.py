import asyncio
import os
from aiogram import Bot, Dispatcher
from handlers import router
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from plant_storage import get_today_plans

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
dp.include_router(router)

USER_CHAT_ID = int(os.getenv("USER_CHAT_ID", "0"))

async def send_daily_reminder():
    if USER_CHAT_ID == 0:
        print("USER_CHAT_ID не задан.")
        return
    plants = get_today_plans()
    if not plants:
        await bot.send_message(USER_CHAT_ID, "Сегодня поливать ничего не нужно.")
    else:
        text = "\n".join(f"• {p['name']}" for p in plants)
        await bot.send_message(USER_CHAT_ID, f"Напоминание!\nСегодня поливаем:\n{text}")

async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_daily_reminder, trigger="cron", hour=8, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
