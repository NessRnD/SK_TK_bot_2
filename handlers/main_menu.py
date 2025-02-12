import datetime
import logging

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale

import config
import states
import text
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


@router.message(Command("admin"))
async def admin(msg: Message, state: FSMContext):
    await msg.answer(f"Добро пожаловать в меню администратора!", parse_mode=ParseMode.HTML, reply_markup=kb.admin_menu)
    await state.set_state(states.AdminMenu.admin)

@router.message(Work.main_state)
async def set_name(msg: Message, state: FSMContext):
    if db.user_exists(msg.from_user.id):
        if msg.text == 'Получить номер предписания':
            old_number = config.counter.get_value()
            new_number = config.counter.new_value()
            logging.info(old_number)
            logging.info(new_number)
            answer = "Ваш номер предписания: №" + str(new_number)

            config.save_number(str(config.counter.get_value()))
            file_l = open('user_log.txt', "a+", encoding="utf-8")
            file_l.write('Номер:' + str(config.counter.get_value()) +
                         '  ' + 'Взял:' + db.get_name(msg.from_user.id) +
                         '  ' + 'Время:' + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + '\n')
            file_l.close()
            await msg.answer(answer, parse_mode=ParseMode.HTML)
        if msg.text == 'Справка':
            await msg.answer(text='\n'.join(text.info), parse_mode=ParseMode.HTML)
        if msg.text == 'Заполнить расстановку':
            await msg.answer("<b>Меню расстановки:</b>", parse_mode=ParseMode.HTML,
                             reply_markup=kb.pos_menu)
            await state.set_state(Work.fill_placement)
        if msg.text == 'Проверить расстановку':
            await msg.answer('Проверить расстановку')
    else:
        await msg.answer("<b>Вы не зарегестрированы</b>", parse_mode=ParseMode.HTML)
        await state.clear()

@router.message(Work.fill_placement, F.text)
async def fill_placement(msg: Message, state: FSMContext):
    if msg.text == "Назад":
        await  msg.answer("<b>Главное меню:</b>", parse_mode=ParseMode.HTML,
                               reply_markup=kb.main_menu)
        await state.set_state(Work.main_state)
    if msg.text == "Производственный статус":
        await  msg.answer("<b>Производственный статус:</b>", parse_mode=ParseMode.HTML,
                               reply_markup=kb.pro_menu)
        await state.update_data(fill_placement=msg.text)
        await state.set_state(Work.placement_proizvodstvo)
    if msg.text == "Непроизводственный статус":
        await  msg.answer("<b>Непроизводственный статус:</b>", parse_mode=ParseMode.HTML,
                               reply_markup=kb.nopro_menu)
        await state.update_data(fill_placement=msg.text)
        await state.set_state(Work.placement_neproizvodstvo)

@router.message(Work.placement_proizvodstvo, F.text)
async def proizvodstvo(msg: Message, state: FSMContext):
    if msg.text == "Назад":
        await msg.answer("<b>Меню расстановки:</b>", parse_mode=ParseMode.HTML,
                         reply_markup=kb.pos_menu)
        await state.set_state(Work.fill_placement)
    #кнопка "Заполнить как за предыдущий день"
    if msg.text == "Заполнить как за предыдущий день":
        rows = db.get_my_rasstanovka(msg.from_user.id, config.get_date(days_ago=1))
        if rows:
            # Форматируем результат
            response = "Ваша расстановка:\n"
            for row in rows:
                response += (f"<b>Расстановка за вчера:</b> ID Объекта: {row[2]}, "
                             f"Категория: {row[3]}, Вид ИИ: {row[4]}, Статус: {row[5]}, Дата: {row[6]}\n")
            await msg.answer(response, parse_mode=ParseMode.HTML)
            for row in rows:
                db.add_pos(row[1],
                           row[2],
                           row[3],
                           row[4],
                           row[5],
                           config.get_date())
            await msg.answer( "<b>Расстановка обновлена:</b>", parse_mode=ParseMode.HTML)
            await msg.answer( "<b>Меню расстановки:</b>", parse_mode=ParseMode.HTML,
                                   reply_markup=kb.pos_menu)
            await state.set_state(Work.fill_placement)
        else:
            await msg.answer( "<b>Записей не найдено!</b>", parse_mode=ParseMode.HTML)
    #кнопка "Выбрать объект"
    if msg.text == "Выбрать объект":
        await msg.answer( "<b>Введите шестизначный ID объекта:</b>",
                               parse_mode=ParseMode.HTML,
                               reply_markup=kb.sel_obj_menu)
        await state.set_state(Work.placement_proizvodstvo_select_obj)

@router.message(Work.placement_proizvodstvo_select_obj, F.text)
async def select_obj(msg: Message, state: FSMContext):
    if msg.text == "Назад":
        logging.info(f"nazad: {msg.text}")
        await msg.answer( "<b>Меню расстановки:</b>", parse_mode=ParseMode.HTML,
                               reply_markup=kb.pos_menu)
        await state.set_state(Work.fill_placement)
    else:
        obj = config.check_six_digit_number(msg.text)
        if obj == 0:
            await msg.answer("<b>Введен некорреткный индекс:</b>",
                                   parse_mode=ParseMode.HTML)
        else:
            await state.update_data(placement_proizvodstvo_select_obj=obj)
            data = await state.get_data()
            msg_text = f'Вы выбрали объект <b>{data.get("placement_proizvodstvo_select_obj")}</b>'
            await msg.answer( msg_text, parse_mode=ParseMode.HTML)
            await msg.answer( "<b>Выберите контролируемый вид изысканий:</b>",
                                   parse_mode=ParseMode.HTML,
                                   reply_markup=kb.viborii_menu)
            await state.set_state(Work.placement_proizvodstvo_vibor_ii)

@router.message(Work.placement_proizvodstvo_vibor_ii, F.text)
async def vibor_ii(msg: Message, state: FSMContext):
    if msg.text == "Назад":
        await msg.answer("<b>Меню расстановки:</b>", parse_mode=ParseMode.HTML,
                               reply_markup=kb.pos_menu)
        await state.set_state(Work.fill_placement)

    if msg.text in ["ИГИ", "ИГДИ", "ИГМИ", "ИЭИ"]:
        await state.update_data(placement_proizvodstvo_vibor_ii=msg.text)
        data = await state.get_data()
        msg_text = f'Вы выбрали вид изысканий <b>{data.get("placement_proizvodstvo_vibor_ii")}</b>'
        await msg.answer( msg_text, parse_mode=ParseMode.HTML)
        await msg.answer( "<b>Укажите вид работ:</b>", parse_mode=ParseMode.HTML,
                               reply_markup=kb.vibor_vid_menu)
        await state.set_state(Work.placement_proizvodstvo_vibor_vid_rabot)

@router.message(Work.placement_proizvodstvo_vibor_vid_rabot, F.text)
async def vibor_vid_rabot(msg: Message, state: FSMContext):
    if msg .text == "Назад":
        await msg.answer( "<b>Меню расстановки:</b>", parse_mode=ParseMode.HTML,
                               reply_markup=kb.pos_menu)
        await state.set_state(Work.fill_placement)

    if msg.text in ['Подготовительный: проверка ТЗ (первичное)',
                        'Подготовительный: проверка ТЗ (повторное)',
                        'Подготовительный: проверка ППР (первичное)',
                        'Подготовительный: проверка ППР (повторное)',
                        'Полевой этап (дистанционно)',
                        'Полевой этап',
                        'Лабораторный этап (дистанционно)',
                        'Лабораторный этап',
                        'Камеральный: проверка ТО (первичное)',
                        'Камеральный: проверка ТО (повторное)']:
        await state.update_data(placement_proizvodstvo_vibor_vid_rabot=msg.text)
        data = await state.get_data()
        msg_text = f'Вы выбрали вид работ <b>{data.get("placement_proizvodstvo")}</b> <b>{data.get("placement_proizvodstvo_vibor_vid_rabot")}</b> '
        await msg.answer( msg_text, parse_mode=ParseMode.HTML)
        msg_text = (f'Ваш статус сегодня: <b>{data.get("fill_placement")}</b> Объект:<b>{data.get("placement_proizvodstvo_select_obj")}</b> '
                    f'Вид ИИ: <b>{data.get("placement_proizvodstvo_vibor_ii")}</b> Вид работ: <b>{data.get("placement_proizvodstvo_vibor_vid_rabot")}</b>')
        # запись в БД
        await msg.answer( msg_text, parse_mode=ParseMode.HTML)
        db.add_pos(msg.from_user.id,
                   data.get("placement_proizvodstvo_select_obj"),
                   data.get("fill_placement"),
                   data.get("placement_proizvodstvo_vibor_ii"),
                   data.get("placement_proizvodstvo_vibor_vid_rabot"),
                   config.get_date())
        await msg.answer("<b>Заполнение производственного статуса:</b>",
                               parse_mode=ParseMode.HTML, reply_markup=kb.pro_menu)
        await state.set_state(Work.fill_placement)

@router.message(Work.placement_neproizvodstvo, F.text)
async def ne_proizvodstvo(msg: Message, state: FSMContext):
    if msg.text == "Назад":
        await msg.answer("<b>Меню расстановки:</b>", parse_mode=ParseMode.HTML,
                         reply_markup=kb.pos_menu)
        await state.set_state(Work.fill_placement)
    if msg.text == "Заполнить как за предыдущий день":
        rows = db.get_my_rasstanovka(msg.from_user.id, config.get_date(days_ago=1))
        today_rows = db.get_my_rasstanovka(msg.from_user.id, config.get_date())
        if not today_rows:
            if rows:
                response = "Ваша расстановка:\n"
                count = 0
                # Форматируем результат
                for row in rows:
                    if row[3] == "Производственный":
                        count += 1
                if count > 0:
                    await msg.answer("<b>Одна или несколько записей расстановки за вчерашний день"
                                           "заполена как производственный статус, расстановку необходимо заполнить заново!</b>",
                                           parse_mode=ParseMode.HTML)
                else:
                    for row in rows:
                        response += (f"<b>Расстановка за вчера:</b> ID Объекта: {row[2]}, "
                                     f"Категория: {row[3]}, Вид ИИ: {row[4]}, Статус: {row[5]}, Дата: {row[6]}\n")
                        db.add_pos(row[1],
                                   row[2],
                                   row[3],
                                   row[4],
                                   row[5],
                                   config.get_date())
                    await msg.answer("<b>Расстановка обновлена:</b>", parse_mode=ParseMode.HTML)
                    await msg.answer( "<b>Меню расстановки:</b>", parse_mode=ParseMode.HTML)
                    await msg.answer( response, parse_mode=ParseMode.HTML,
                                           reply_markup=kb.pos_menu)
                    await state.set_state(Work.fill_placement)
            else:
                await msg.answer( "<b>Записей не найдено!</b>", parse_mode=ParseMode.HTML)
        else:
            await msg.answer( "<b>У Вас уже есть статус на сегодня</b>", parse_mode=ParseMode.HTML)


    if msg.text in ["Работа в офисе"]:
        db.add_pos(msg.from_user.id,
                   "-",
                   "Непроизводственный",
                   "-",
                   msg.text,
                   config.get_date())
        msg_text = (f'Ваш статус сегодня: <b>"Непроизводственный"</b> Объект:<b>"-"</b> '
                    f'Вид ИИ: <b>"-"</b> Вид работ: <b>{msg.text}</b>')
        await msg.answer( msg_text, parse_mode=ParseMode.HTML,
                               reply_markup=kb.pos_menu)
        await state.set_state(Work.fill_placement)

    if msg.text in ["Отпуск", "Больничный", "Обучение", "Межвахта"]:
        await state.update_data(placement_neproizvodstvo=msg.text)
        await msg.reply(f"Hello, <b>{msg.from_user.full_name}!</b> Выберите дату")
        await state.set_state(Work.placement_neproizvodstvo_start_date)
        await msg.answer("Выберите дату начала:", parse_mode=ParseMode.HTML,
                             reply_markup=await SimpleCalendar(
                                 locale=await get_user_locale(msg.from_user)).start_calendar())

@router.callback_query(Work.placement_neproizvodstvo_start_date, SimpleCalendarCallback.filter())
async def set_start_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )

    if callback_data.act == 'CANCEL':
        await callback_query.message.answer("Вы отменили выбор даты.", parse_mode=ParseMode.HTML,
                                            reply_markup=kb.nopro_menu)
        await state.set_state(Work.placement_neproizvodstvo)

    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'Дата начала: {date.strftime("%d/%m/%Y")}'
        )
        await state.update_data(placement_neproizvodstvo_start_date=date.strftime("%d/%m/%Y"))
        await state.set_state(Work.placement_neproizvodstvo_end_date)
        await callback_query.message.answer("Выберите дату окончания:", parse_mode=ParseMode.HTML,
                             reply_markup=await SimpleCalendar(
                                 locale=await get_user_locale(callback_query.from_user)).start_calendar())

@router.callback_query(Work.placement_neproizvodstvo_end_date, SimpleCalendarCallback.filter())
async def set_end_date(callback_query: CallbackQuery, callback_data: CallbackData,
                                  state: FSMContext):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )

    if callback_data.act == 'CANCEL':
        await callback_query.message.answer("Вы отменили выбор даты.", parse_mode=ParseMode.HTML,
                                            reply_markup=kb.nopro_menu)
        await state.set_state(Work.placement_neproizvodstvo)

    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'Дата окончания: {date.strftime("%d/%m/%Y")}'
        )
        await state.update_data(placement_neproizvodstvo_end_date=date.strftime("%d/%m/%Y"))
        data = await state.get_data()
        start_date = datetime.datetime.strptime(data.get("bot_pos_nopro_date_start"), "%d/%m/%Y")
        end_date = datetime.datetime.strptime(data.get("bot_pos_nopro_date_end"), "%d/%m/%Y")
    if end_date<start_date:
        await callback_query.message.answer(
            f'Дата окончания: {end_date} не может быть раньше даты начала {start_date}'
        )
        await state.set_state(Work.placement_neproizvodstvo_end_date)
        await callback_query.message.answer("Выберите дату окончания:", parse_mode=ParseMode.HTML,
                                            reply_markup=await SimpleCalendar(
                                                locale=await get_user_locale(
                                                    callback_query.from_user)).start_calendar())
    else:
        current_date = start_date
        while current_date <= end_date:
            db.add_pos(
                callback_query.from_user.id,
                "-",
                "Непроизводственный",
                "-",
                data.get("bot_pos_nopro"),
                current_date.strftime("%d.%m.%Y")
            )
            current_date += datetime.timedelta(days=1)

        await callback_query.message.answer( "<b>Непроизводственный статус:</b>", parse_mode=ParseMode.HTML,
                               reply_markup=kb.nopro_menu)
        await state.update_data(bot_pos="Непроизводственный")
        await state.set_state(Work.placement_neproizvodstvo)

@router.message()
async def no_state(msg: Message, state: FSMContext):
    if not db.user_exists(msg.from_user.id):
        await msg.answer(f"Видимо бот был перезапущен, чтобы войти в главное меню направьте сообщение: /start",
                         parse_mode=ParseMode.HTML)
