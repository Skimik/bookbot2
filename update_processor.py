import telebot              #весь api tlgrm bot
from db_processor import Database         #самописный модуль
import threading            #многопоточность
import time                 #работа со временем
import json
from fsm import Fsm
from datetime import datetime
from pprint import pprint, pformat

bot = telebot.TeleBot('1294566396:AAFB5aer0PWXnVhPHSr0CFX1pElg8t5UCHs')

while True:
    start = time.time()
    update_mes = Database(table_name = 'update_mes').select_db('*')
    if update_mes['available'] != 0:
        print(len(update_mes['result']))
        for i in range(len(update_mes['result'])):
            print(i)
            bot.edit_message_text(chat_id=update_mes['result'][i]['telegram_id'], 
									   message_id = update_mes['result'][i]['mes_id'],
									   text= datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
    time.sleep(5 - (time.time() - start))