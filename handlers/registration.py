import datetime

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import config
import kb
from states import Registration, Work

reg_router = Router()

@reg_router.message(Registration.user_key)
async def registration(msg: Message, state: FSMContext):
    user_pass = msg.text
    file_k = open(config.invite_code)
    key = file_k.read()
    if user_pass == key:
        await msg.answer('<b>Отлично</b>, теперь введите <b>ФИО</b>, в формате <b>Иванов Иван Иванович</b>',
                               parse_mode=ParseMode.HTML)
        await state.set_state(Registration.user_name)
    else:
        await msg.answer('<b>Извините, но у вас нет доступа к боту, введите корректный код ;(</b>', parse_mode=ParseMode.HTML)


@reg_router.message(Registration.user_name)
async def set_name(msg: Message, state: FSMContext):
    config.db.set_name(msg.from_user.id, msg.text)
    config.db.set_signup(msg.from_user.id, "done")
    file_r = open(config.reg_log, "a+", encoding="utf-8")
    file_r.write('Успешно зарегистрировался: ' + config.db.get_name(msg.from_user.id) + ' ' + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + '\n')
    file_r.close()
    await msg.answer("<b>Вы успешно зарегистрировались</b>", parse_mode=ParseMode.HTML, reply_markup=kb.main_menu)
    await state.set_state(Work.main_state)
