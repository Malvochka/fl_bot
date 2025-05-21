
import json
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path("plants.json")
if not DATA_FILE.exists():
    DATA_FILE.write_text("{}", encoding="utf-8")  # Храним словарь {chat_id: [...]}

def _load():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_plant(chat_id, name, interval, start_date):
    data = _load()
    chat_key = str(chat_id)
    if chat_key not in data:
        data[chat_key] = []
    data[chat_key].append({
        "id": len(data[chat_key]),
        "name": name,
        "interval": interval,
        "start_date": start_date.isoformat()
    })
    _save(data)

def list_plants(chat_id):
    return _load().get(str(chat_id), [])

def update_plant(chat_id, plant_id, name=None, interval=None, start_date=None):
    data = _load()
    plants = data.get(str(chat_id), [])
    for plant in plants:
        if plant["id"] == plant_id:
            if name: plant["name"] = name
            if interval: plant["interval"] = interval
            if start_date: plant["start_date"] = start_date.isoformat()
            break
    data[str(chat_id)] = plants
    _save(data)

def delete_plant(chat_id, plant_id):
    data = _load()
    plants = data.get(str(chat_id), [])
    plants = [p for p in plants if p["id"] != plant_id]
    data[str(chat_id)] = plants
    _save(data)

def get_today_plans(chat_id):
    today = datetime.now().date()
    return [
        plant for plant in list_plants(chat_id)
        if (today - datetime.fromisoformat(plant["start_date"]).date()).days % int(plant["interval"]) == 0
    ]

def get_week_plans(chat_id):
    today = datetime.now().date()
    week = []
    for i in range(7):
        date = today + timedelta(days=i)
        day_plants = [
            plant["name"] for plant in list_plants(chat_id)
            if (date - datetime.fromisoformat(plant["start_date"]).date()).days % int(plant["interval"]) == 0
        ]
        week.append((date.strftime('%A %d.%m'), day_plants))
    return week
