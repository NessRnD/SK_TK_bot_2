from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

#global buttons
button_exit = KeyboardButton(text='Вернуться в главное меню')
button_back = KeyboardButton(text='Назад')
button_accept = KeyboardButton(text='Подтвердить')

#main menu
#buttons
button_get = KeyboardButton(text='Получить номер предписания')
button_pos = KeyboardButton(text='Заполнить расстановку')
button_my_pos = KeyboardButton(text='Проверить расстановку')
button_inf = KeyboardButton(text='Справка')

main_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [button_get],
    [button_pos],
    [button_my_pos],
    [button_inf]
])

#admin menu
button_delete = KeyboardButton(text='Удалить номер предписания')
button_log = KeyboardButton(text='Журнал логов')
button_db = KeyboardButton(text='Скачать БД')
button_del = KeyboardButton(text='Удалить пользователя')
button_null = KeyboardButton(text='Сбросить номер предписания')
button_reg = KeyboardButton(text='Логи регистрации')
button_generate = KeyboardButton(text='Сгенерировать код')
button_check = KeyboardButton(text='Посмотреть код')

#inline_buttons
ikb_delete = InlineKeyboardButton(text='Подтвердить',callback_data='Подтвердить')
ikb_cancel = InlineKeyboardButton(text='Отмена',callback_data='Отмена')

ikb_remove = InlineKeyboardButton(text='Удалить пользователя',callback_data='Удалить пользователя')

#menus setup
admin_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [button_delete, button_del],
    [button_db, button_log],
    [button_check, button_reg],
    [button_generate],
    [button_exit]
])