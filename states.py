from aiogram.fsm.state import State, StatesGroup

class AddReminder(StatesGroup):
    waiting_for_content = State()
    waiting_for_date = State()
    waiting_for_time = State()

class EditReminder(StatesGroup):
    waiting_for_id = State()
    waiting_for_action = State()
    waiting_new_date = State()
    waiting_new_time = State()
    waiting_new_content = State()

class DeleteReminder(StatesGroup):
    waiting_for_id = State()
