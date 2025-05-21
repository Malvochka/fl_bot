import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
from plant_storage import _load, get_today_plans
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

def schedule_daily_reminders():
    data = _load()
    for chat_id, plants in data.items():
        for plant in plants:
            remind_time = plant.get("remind_time", "08:00")
            hour, minute = map(int, remind_time.split(":"))
            plant_name = plant["name"]

            def make_task(cid, name):
                async def task():
                    today_plants = get_today_plans(cid)
                    if any(p["name"] == name for p in today_plants):
                        await bot.send_message(cid, f"🔔 Напоминание: пора поливать {name}")
                return task

            scheduler.add_job(make_task(int(chat_id), plant_name), CronTrigger(hour=hour, minute=minute))

async def main():
    schedule_daily_reminders()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())