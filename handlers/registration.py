import datetime
import logging

from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F

import config
import kb
import text
from states import Registration, Work

reg_router = Router()

@reg_router.message(Command(commands=["start"]))
async def cmd_start(msg: Message, state: FSMContext):
    logging.info("Command /start received in registration")
    if not config.db.user_exists(msg.from_user.id):
        logging.info(f"user not exist")
        config.db.add_user(msg.from_user.id)
        config.db.set_tgtag(msg.from_user.id, msg.from_user.username)
        await msg.answer(text='\n'.join(text.invite_msg), parse_mode=ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Registration.user_key)
    elif config.db.get_signup(msg.from_user.id) == "setname":
        await msg.answer(text='\n'.join(text.key_query), parse_mode=ParseMode.HTML)
        await state.set_state(Registration.user_key)
    else:
        await msg.answer("<b>Главное меню</b>", parse_mode=ParseMode.HTML, reply_markup=kb.main_menu)
        await state.set_state(Work.main_state)

@reg_router.message(Registration.user_key, F.text)
async def registration(msg: Message, state: FSMContext):
    logging.info(f"User key received: {msg.text}")
    user_pass = msg.text
    with open(config.invite_code, 'r') as file_k:
        key = file_k.read().strip()
    logging.info(f"Expected key: {key}")
    if user_pass == key:
        logging.info("Key matched")
        await msg.answer('<b>Отлично</b>, теперь введите <b>ФИО</b>, в формате <b>Иванов Иван Иванович</b>',
                        parse_mode=ParseMode.HTML)
        await state.set_state(Registration.user_name)
    else:
        logging.info("Key did not match")
        await msg.answer('<b>Извините, но у вас нет доступа к боту, введите корректный код ;(</b>', parse_mode=ParseMode.HTML)

@reg_router.message(Registration.user_name, F.text)
async def set_name(msg: Message, state: FSMContext):
    logging.info(f"User name received: {msg.text}")
    config.db.set_name(msg.from_user.id, msg.text)
    config.db.set_signup(msg.from_user.id, "done")
    with open(config.reg_log, "a+", encoding="utf-8") as file_r:
        file_r.write('Успешно зарегистрировался: ' + config.db.get_name(msg.from_user.id) + ' ' + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + '\n')
    await msg.answer("<b>Вы успешно зарегистрировались</b>", parse_mode=ParseMode.HTML, reply_markup=kb.main_menu)
    await state.set_state(Work.main_state)
