from aiogram.fsm.state import State, StatesGroup

#main_menu
class Registration(StatesGroup):
    user_key = State()
    user_name = State()

class Work(StatesGroup):
    main_state = State()

#admin_menu
class AdminMenu(StatesGroup):
    admin = State()

#help_menu
class HelpMenu(StatesGroup):
    help = State()