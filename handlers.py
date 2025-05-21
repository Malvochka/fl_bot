
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from plant_storage import add_plant, delete_plant, update_plant, list_plants, get_today_plans, get_week_plans
from states import PlantForm
from keyboards import main_menu, calendar_menu, generate_edit_menu
from datetime import datetime
from zoneinfo import ZoneInfo
import re

router = Router()

@router.message(F.text == "/start")
async def start(message: Message):
    photo = FSInputFile("welcome.jpg")
    await message.answer_photo(photo, caption="Привет! Я бот-помощник для полива растений. Что будем делать?", reply_markup=main_menu)

@router.message(F.text == "📅 Календарь")
async def calendar(message: Message):
    await message.answer("Выберите:", reply_markup=calendar_menu)

@router.message(F.text == "Сегодня")
async def today(message: Message):
    today_plants = get_today_plans(message.chat.id)
    if today_plants:
        text = "\n".join(f"• {p['name']}" for p in today_plants)
        await message.answer(f"Сегодня поливаем:\n{text}")
    else:
        await message.answer("Сегодня поливать ничего не нужно.")

@router.message(F.text == "Неделя")
async def week(message: Message):
    week = get_week_plans(message.chat.id)
    reply = ""
    for day, items in week:
        plants = ", ".join(items) if items else "—"
        reply += f"{day}: {plants}\n"
    await message.answer(reply)

@router.message(F.text == "🌱 Добавить растение")
async def add_plant_start(message: Message, state: FSMContext):
    await state.set_state(PlantForm.name)
    await message.answer("Введите название растения:")

@router.message(PlantForm.name)
async def plant_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(PlantForm.interval)
    await message.answer("Сколько дней между поливами?")

@router.message(PlantForm.interval)
async def plant_interval(message: Message, state: FSMContext):
    try:
        interval = int(message.text)
        await state.update_data(interval=interval)
        await state.set_state(PlantForm.start_date)
        await message.answer("Дата начала полива? (введите 'сегодня' или ГГГГ-ММ-ДД)")
    except:
        await message.answer("Введите число дней, например: 3")

@router.message(PlantForm.start_date)
async def plant_start_date(message: Message, state: FSMContext):
    try:
        user_input = message.text.strip()
        if user_input == "" or user_input.lower() in ["сегодня", "now"]:
            start_date = datetime.now(ZoneInfo("Europe/Moscow")).date()
        else:
            start_date = datetime.strptime(user_input, "%Y-%m-%d").date()
        await state.update_data(start_date=start_date)
        await state.set_state(PlantForm.remind_time)
        await message.answer("Во сколько напоминать? Введите в формате ЧЧ:ММ")
    except:
        await message.answer("Введите дату в формате: 2025-05-01 или просто отправьте 'сегодня'")

@router.message(PlantForm.remind_time)
async def remind_time(message: Message, state: FSMContext):
    time_pattern = r'^([01]?\d|2[0-3]):([0-5]\d)$'
    user_input = message.text.strip()
    match = re.match(time_pattern, user_input)

    if not match:
        await message.answer("Введите время в формате ЧЧ:ММ (например, 08:00 или 20:45)")
        return

    hours, minutes = map(int, match.groups())
    remind_at = f"{hours:02d}:{minutes:02d}"
    await state.update_data(remind_time=remind_at)

    data = await state.get_data()
    add_plant(message.chat.id, data['name'], data['interval'], data['start_date'], remind_at)
    await message.answer(f"Растение добавлено! Напоминание будет приходить в {remind_at}", reply_markup=main_menu)
    await state.clear()

@router.message(F.text == "✏ Изменить график полива")
async def edit_menu(message: Message):
    plants = list_plants(message.chat.id)
    if not plants:
        await message.answer("Пока нет ни одного растения.")
        return
    await message.answer("Выберите растение для редактирования или удаления:", reply_markup=generate_edit_menu(plants))

@router.callback_query(F.data.startswith("delete_"))
async def delete_plant_handler(callback: CallbackQuery):
    plant_id = int(callback.data.split("_")[1])
    delete_plant(plant_id)
    await callback.message.edit_text("Удалено.")
    await callback.answer()

@router.callback_query(F.data.startswith("edit_"))
async def edit_plant_handler(callback: CallbackQuery, state: FSMContext):
    plant_id = int(callback.data.split("_")[1])
    await state.set_state(PlantForm.name)
    await state.update_data(editing_id=plant_id)
    await callback.message.answer("Введите новое название растения:")
    await callback.answer()

@router.message(F.text == "⬅ Назад")
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Возвращаемся в главное меню.", reply_markup=main_menu)
