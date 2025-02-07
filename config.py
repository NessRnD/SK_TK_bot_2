import os
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



def load_number():
    try:
        with open(num_log, 'r') as f:
            get_number = f.read().strip()
            return int(get_number)
    except FileNotFoundError:
        return 0
    except ValueError:
        return 0

counter = increment_counter()
counter.set_value(load_number())