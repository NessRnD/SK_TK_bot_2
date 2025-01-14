from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import kb
import states

router = Router()


@router.message(StateFilter(states.AdminMenu.admin))
async def admin_menu_state(message: Message):
    await message.answer("Вы находитесь в меню админа.")

@router.message(Command(commands=["Вернуться в главное меню"]))
async def start(msg: Message, state: FSMContext):
        await msg.answer("<b>Вы в главном меню.</b>", parse_mode=ParseMode.HTML, reply_markup=kb.main_menu)
        await state.set_state(states.Work.main_state)
