import datetime

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode


import config
import states
import text
from handlers.registration import registration
from states import Registration, Work

db = config.db
import kb

router = Router()

@router.message(Command("get_state"))
async def get_current_state(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await msg.reply("You are not in any state.")
    else:
        await msg.reply(f"You are in the state: {current_state}")

@router.message(Command("start"))
async def start(msg: Message, state: FSMContext):
    await state.clear()
    if not db.user_exists(msg.from_user.id):
        db.add_user(msg.from_user.id)
        db.set_tgtag(msg.from_user.id, msg.from_user.username)
        await  msg.answer(text='\n'.join(text.invite_msg), parse_mode=ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Registration.user_key)
    elif db.get_signup(msg.from_user.id) == "setname":
        await state.set_state(Registration.user_key)
        await msg.answer(text='\n'.join(text.key_query), parse_mode=ParseMode.HTML)
    else:
        await msg.answer("<b>Главное меню</b>", parse_mode=ParseMode.HTML, reply_markup=kb.main_menu)
        await state.set_state(Work.main_state)

@router.message(Command("admin"))
async def admin(msg: Message, state: FSMContext):
    await msg.answer(f"Добро пожаловать в меню администратора!", parse_mode=ParseMode.HTML, reply_markup=kb.admin_menu)
    await state.set_state(states.AdminMenu.admin)


@router.message(Work.main_state)
async def set_name(msg: Message, state: FSMContext):
    if db.user_exists(msg.from_user.id):
        if msg.text == 'Получить номер предписания':
            answer = "Ваш номер предписания: №" + str(config.counter.new_value())
            config.save(str(config.counter.get_value()))
            file_l = open('user_log.txt', "a+", encoding="utf-8")
            file_l.write('Номер:' + str(config.counter.get_value()) +
                         '  ' + 'Взял:' + db.get_name(msg.from_user.id) +
                         '  ' + 'Время:' + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + '\n')
            file_l.close()
            await msg.answer(answer, parse_mode=ParseMode.HTML)
        if msg.text == 'Справка':
            await msg.answer(text='\n'.join(text.info), parse_mode=ParseMode.HTML)
        if msg.text == 'Заполнить расстановку':
            await msg.answer('Заполнить расстановку')
        if msg.text == 'Проверить расстановку':
            await msg.answer('Проверить расстановку')
    else:
        await msg.answer("<b>Вы не зарегестрированы</b>", parse_mode=ParseMode.HTML)
        await state.clear()

@router.message()
async def no_state(msg: Message, state: FSMContext):
    if not db.user_exists(msg.from_user.id):
        await msg.answer(f"Видимо бот был перезапущен, чтобы войти в главное меню направьте сообщение: /start",
                         parse_mode=ParseMode.HTML)