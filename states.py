from aiogram.fsm.state import State, StatesGroup

#main_menu
class Registration(StatesGroup):
    user_key = State()
    user_name = State()

class Work(StatesGroup):
    main_state = State()
    fill_placement = State() # выбор статуса (производственный/непроизводственный)
    # запонение производственного статуса
    placement_proizvodstvo = State()
    placement_proizvodstvo_select_obj = State() # ввод id объекта
    placement_proizvodstvo_vibor_ii = State() # выбор вида ИИ
    placement_proizvodstvo_vibor_vid_rabot = State() # выбор вида работ
    # запонение непроизводственного статуса
    placement_neproizvodstvo = State()
    placement_neproizvodstvo_start_date = State()
    placement_neproizvodstvo_end_date = State()

#admin_menu
class AdminMenu(StatesGroup):
    admin = State()

#help_menu
class HelpMenu(StatesGroup):
    help = State()