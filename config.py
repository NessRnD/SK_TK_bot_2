import os
from datetime import date, timedelta
import re

from numb_generator import increment_counter

from db import database

BOT_TOKEN = '7636235626:AAGYrgmpGiILdHavPFDvL2yp4_a_UlIXCRs'
admin_ids = [977050266, 1849857447, 81061749]
current_directory = os.getcwd()
db = database(os.path.join(current_directory, 'database.db'))
invite_code = os.path.join(current_directory, "invite_code.txt")
reg_log = os.path.join(current_directory, "reg_log.txt")
num_log = os.path.join(current_directory, "log.txt")





# func to save numb
def save_number(x):
    f = open(num_log, 'w+')
    f.write(x)
    f.close()

def get_date(days_ago=0):
    today = date.today()
    target_date = today - timedelta(days=days_ago)
    return target_date.strftime("%d.%m.%Y")


def load_number():
    try:
        with open(num_log, 'r') as f:
            get_number = f.read().strip()
            return int(get_number)
    except FileNotFoundError:
        return 0
    except ValueError:
        return 0

def check_six_digit_number(message):
    match = re.search(r'\b\d{6}\b', message)  # Ищем шестизначное число, окруженное границами слов
    if match:
        return int(match.group(0))  # Преобразуем найденное число в целое
    else:
        return 0  # Возвращаем 0, если число не найдено

counter = increment_counter()
counter.set_value(load_number())