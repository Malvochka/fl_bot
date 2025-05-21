from aiogram.fsm.state import State, StatesGroup

class PlantForm(StatesGroup):
    name = State()
    interval = State()
    start_date = State()
