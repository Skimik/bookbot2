
import telebot              #весь api tlgrm bot
import os.path
import requests             #зачем оно здесь, я не знаю, так было в гайде
import pymysql              #на всякий случай
from db_processor import Database         #самописный модуль
import threading            #многопоточность
import time                 #работа со временем
import json
from fsm import Fsm
from datetime import datetime
from pprint import pprint, pformat

fsm_dict = {'1' : Fsm.register_1
		  
		  }

ddos_timer = 1
pass_timer = 300


print('allah')

bot = telebot.TeleBot('1294566396:AAFB5aer0PWXnVhPHSr0CFX1pElg8t5UCHs')

token = "4cfd3ed6dc6fb4fb7968aa8d01cefe934a9a479485467ea8efc54eb65293934f933619e2956fb331d9056"

#vk = vk_session.get_api()
#longpoll = VkBotLongPoll(vk_session, "163796130")

#мне нужно написать хендлер для сообщений.  надо понять как работают классы.
#видимо, тут им и место
class Sendler:
	def __init__(self, id, message, role):
		self.id = id


#def send_vk(id=[], message='сообщение по умолчанию'):
def send_tg(id=[], message='сообщение по умолчанию'):
	if type(id) == list:
		if len(id) == 1:
			bot.send_message(id[0], message)
	else:
		bot.send_message(id, message)



def check_bot(message):
		if message.json['from']['is_bot'] == True:
			bot.message = bot.edit_message_text
			work = True
		elif message.json['from']['is_bot'] == False:
			bot.message = bot.send_message
			work = True
		else:
			bot.send_message(chat_id = 192105252, text = 'чувак, пиздец, вот запрос\n{}\nя вообще бля не ебу что делать спасай нахуй'.format(message))
			work = False
		return work



def stop_ddos(message, ddos_timer=ddos_timer):
	print('------------check DDoS---------------')
	print(message.json['from']['is_bot'])
	if message.json['from']['is_bot'] == False:
		Database(table_name = 'user_db').update_db('last_mes_user_id',
												   '{}'.format(message.message_id),
												   'where telegram_id = {}'.format(message.chat.id))
		print('/////////////////////////////////////////////////')
	if (datetime.now() - Database(table_name = 'user_db').select_db('reg_time','where telegram_id = {}'.format(message.chat.id))['result'][0]['reg_time']).total_seconds() >= 10:
		if (datetime.now() - Database(table_name = 'user_db').select_db('last_mes_time','where telegram_id = {}'.format(message.chat.id))['result'][0]['last_mes_time']).total_seconds() <= ddos_timer:
			print('------------DDoS---------------')
			Database(table_name = 'user_db').update_db('last_mes_time',
													   '"{}"'.format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),
													   'where telegram_id = {}'.format(message.chat.id))
			work = False
		else: 
			print('------------no DDoS---------------')
			work = True
	else: 
		print('------------New User---------------')
		work = True
	return work

def user_checker(message):
	print('------------1==============')
	if Database(table_name = 'user_db').select_db('telegram_id','where telegram_id = {}'.format(message.chat.id))['available'] == 0:
		print('------------2==============')
		Fsm().register(message)
		keyboard_test = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)

def pass_cheсker(message, pass_timer=pass_timer):
	print('------------check pass---------------')
	print(message)	
	if Database(table_name = 'user_db').select_db('pass','where telegram_id = {}'.format(message.chat.id))['result'][0]['pass'] != 'None':
		if (datetime.now() - Database(table_name = 'user_db').select_db('last_mes_time','where telegram_id = {}'.format(message.chat.id))['result'][0]['last_mes_time']).total_seconds() >= pass_timer:
			if Database(table_name = 'user_db').select_db('pass_count','where telegram_id = {}'.format(message.chat.id))['result'][0]['pass_count'] == 0:
				bot.send_message(chat_id = message.chat.id, text='тебя не было в системе больше 5 минут. введи пароль для дальнейших действий')
				Database(table_name = 'user_db').update_db('pass_count',
															'1',
															'where telegram_id = {}'.format(message.chat.id))
				print('------------3---------------')
			if message.text == Database(table_name = 'user_db').select_db('pass','where telegram_id = {}'.format(message.from_user.id))['result'][0]['pass']:
				
				bot.send_message(chat_id = message.chat.id, text="пароль верный. доступ открыт")
				Database(table_name = 'user_db').update_db('pass_count',
															'1',
															'where telegram_id = {}'.format(message.chat.id))
				Database(table_name = 'user_db').update_db('last_mes_time',
												   '"{}"'.format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),
												   'where telegram_id = {}'.format(message.chat.id))
				print('------------1---------------')
				return True
			else: 
				bot.send_message(chat_id = message.chat.id, text="пароль неверный")
				print('------------2---------------')
				return False
		else: 
			Database(table_name = 'user_db').update_db('last_mes_time',
												   '"{}"'.format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),
												   'where telegram_id = {}'.format(message.chat.id))
			return True
	else:
		Database(table_name = 'user_db').update_db('last_mes_time',
												   '"{}"'.format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),
												   'where telegram_id = {}'.format(message.chat.id))
		print('------------4---------------')
		return True


@bot.message_handler()
def message_handler(message):
	print(message)
	handler(message = message)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
	print(call)
	handler(message = call.message, callback_id = call.id, callback_data = call.data)

def handler(message, callback_id = None, callback_data = None):
	print(message)
	print(callback_id)
	print(callback_data)
	user_checker(message)
	if stop_ddos(message) and pass_cheсker(message):
		Fsm().executor(message, callback_id, callback_data)


print('akbar')
bot.polling()



print('voistinu akbar')