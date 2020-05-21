import telebot
import time
from datetime import datetime
from db_processor import Database


class Fsm():
	def __init__(self, token='1294566396:AAFB5aer0PWXnVhPHSr0CFX1pElg8t5UCHs'):
		self.bot = telebot.TeleBot(token)
		self.keyboard = telebot.types
		self.kb_remove = self.keyboard.ReplyKeyboardRemove
		self.kb_reply = self.keyboard.ReplyKeyboardMarkup
		self.kb_inline = self.keyboard.InlineKeyboardMarkup
		self.btn_inline = self.keyboard.InlineKeyboardButton

		self.commands = {
						'тест':'test',
						'домой': 'home',
						'назад': 'back',
						'пополнение балланса': 'default',
						'демо игра': 'default',
						'личный кабинет': 'default',
						'ставка': 'default',
						'регистрация': 'default',
						'начать': 'start'
						}

#исполнитель запросов
	def executor(self, message, callback_id=None, callback_data=None):
		user_db = Database(table_name = 'user_db').select_db('*','where telegram_id = {}'.format(message.chat.id))

		if message.text.lower() in self.commands:
			print('---------------------------------1-------------------------------------')
			x = getattr(self, self.commands[message.text.lower()])
			x(message, callback_id, callback_data)
		elif user_db['result'][0]['fsm_wait'] != 0:
			print('---------------------------------2-------------------------------------')
			print(Database('fsm').select_db('*','where track = {}'.format(int(user_db['result'][0]['fsm_wait']))))
			x = getattr(self, Database('fsm').select_db('*','where track = {}'.format(user_db['result'][0]['fsm_wait']))['result'][0]['point_b'])
			x(message, callback_id, callback_data)
		
		elif callback_data != None:
			print('---------------------------------3-------------------------------------')
			data = callback_data.split(', ')
			print(data)
			fsm_code = int(data[0])
			fsm_wait = int(data[1])
			fsm_param = str(data[2])
			call_point = Database('fsm').select_db('*','where track = {}'.format(fsm_code))
			db_point = Database('fsm').select_db('*','where track = {}'.format(user_db['result'][0]['fsm_code']))
			if  (call_point['available'] != 0 and db_point['available'] != 0):

				if (call_point['result'][0]['point_a'] == db_point['result'][0]['point_b'] or call_point['result'][0]['point_a'] == "all"):
					x = getattr(self, call_point['result'][0]['point_b'])
					x(message, callback_id, callback_data)
				else: print('--------- ошибка последовательности автоматов. автомат проигнорирован ---------')
			else: print('--------- ошибка наличия автоматов. автомат проигнорирован ---------')
		else: print('--------- ошибка обработки запроса. автомат не выполнен ---------')

		
	def fsm_db(self, message, fsm_code=None, fsm_wait=None, fsm_param=None, callback_data=None):
		if callback_data != None:
			data = callback_data.split(', ')
			fsm_code = int(data[0])
			fsm_wait = int(data[1])
			fsm_param = str(data[2])
		Database(table_name = 'user_db').update_db('fsm_code',
												   '{}'.format(fsm_code),
												   'where telegram_id = {}'.format(message.chat.id))
		Database(table_name = 'user_db').update_db('fsm_wait',
												   '{}'.format(fsm_wait),
												   'where telegram_id = {}'.format(message.chat.id))
		Database(table_name = 'user_db').update_db('fsm_param',
												   '"{}"'.format(fsm_param),
												   'where telegram_id = {}'.format(message.chat.id))

	def send_message(self, message, text, keyboard_reply = None, callback_id=None, callback_data=None):
		msg = self.bot.send_message(chat_id=message.chat.id, 
									text= text,
									reply_markup = keyboard_reply)
		Database(table_name = 'user_db').update_db('last_mes_bot_id',
												   '"{}"'.format(msg.message_id),
												   'where telegram_id = {}'.format(message.chat.id))
		return msg

	def send_reply(self, message, reply_markup, callback_id=None, callback_data=None):
		msg = self.bot.send_message(chat_id=message.chat.id, 
									   
									   text= '________________________________',
									   reply_markup = reply_markup)
		Database(table_name = 'user_db').update_db('last_mes_bot_inline_id',
												   '"{}"'.format(msg.message_id),
												   'where telegram_id = {}'.format(message.chat.id))
		return msg
	
	def edit_message_text(self, message, text, callback_id=None, callback_data=None):
		msg_id = Database(table_name = 'user_db').select_db('*','where telegram_id = {}'.format(message.chat.id))['result'][0]
		msg = None
		if msg_id['last_mes_user_id'] < msg_id['last_mes_bot_id']:
			msg = self.bot.edit_message_text(chat_id=message.chat.id, 
											 message_id = msg_id['last_mes_bot_id'],
											 text= text)
			
			print(msg)
		elif msg_id['last_mes_user_id'] > msg_id['last_mes_bot_id']:
			msg = self.bot.send_message(chat_id=message.chat.id, 
									   
									   text= text)
			Database(table_name = 'user_db').update_db('last_mes_bot_id',
													   '"{}"'.format(msg.message_id),
													   'where telegram_id = {}'.format(message.chat.id))
		return msg

	def edit_message_reply(self, message, text, keyboard_inline, callback_id = None, callback_data = None):
		msg_id = Database(table_name = 'user_db').select_db('*','where telegram_id = {}'.format(message.chat.id))['result'][0]
		if ((message.json['from']['is_bot'] == True) and 
			(message.message_id == msg_id['last_mes_bot_inline_id']) and
			msg_id['last_mes_bot_inline_id'] > msg_id['last_mes_bot_id'] and
			msg_id['last_mes_bot_inline_id'] > msg_id['last_mes_user_id']):

			self.bot.edit_message_text(chat_id=message.chat.id,
									   message_id = message.message_id,
									   text=text, 
									   reply_markup = keyboard_inline)
		else: 
			msg = self.bot.send_message(chat_id=message.chat.id,
										text=text,
										reply_markup = keyboard_inline)
			Database(table_name = 'user_db').update_db('last_mes_bot_inline_id',
													   '"{}"'.format(msg.message_id),
													   'where telegram_id = {}'.format(message.chat.id))

		#msg_id = Database(table_name = 'user_db').select_db('*','where telegram_id = {}'.format(message.chat.id))['result'][0]
		#msg = None
		#try:
		#	if msg_id['last_mes_user_id'] < msg_id['last_mes_bot_id'] and msg_id['last_mes_bot_id'] < msg_id['last_mes_bot_inline_id']:
		#		msg = self.bot.edit_message_reply_markup(chat_id=message.chat.id, 
		#												 message_id = msg_id['last_mes_bot_inline_id'],
		#												 reply_markup = reply_markup)
		#	elif text == None:
		#		msg = self.bot.send_message(chat_id=message.chat.id, 
									   
		#								   text= '________________________________',
		#								   reply_markup = reply_markup)
		#		Database(table_name = 'user_db').update_db('last_mes_bot_inline_id',
		#												   '"{}"'.format(msg.message_id),
		#												   'where telegram_id = {}'.format(message.chat.id))
		#		print(msg)
		#	else:
		#		msg = self.bot.send_message(chat_id=message.chat.id, 
									   
		#								   text= text,
		#								   reply_markup = reply_markup)
		#		Database(table_name = 'user_db').update_db('last_mes_bot_inline_id',
		#												   '"{}"'.format(msg.message_id),
		#												   'where telegram_id = {}'.format(message.chat.id))
		#except:
		#	msg = self.bot.send_message(chat_id=message.chat.id, 
									   
		#								   text= '________________________________',
		#								   reply_markup = reply_markup)
		#	Database(table_name = 'user_db').update_db('last_mes_bot_inline_id',
		#												   '"{}"'.format(msg.message_id),
		#												   'where telegram_id = {}'.format(message.chat.id))
		#	print(msg)
		#return msg

	def cleaner(self):
		pass

	def back(self):
		pass

	def update_mes(self, message, update_types, update_param='None'):
		Database('update_mes').delete_db('where telegram_id = {}'.format(message.chat.id))
		Database('update_mes').insert_db(values = ['{}'.format(message.chat.id),
												   '{}'.format(message.message_id),
												   '{}'.format(update_types),
												   '"{}"'.format(update_param),
												   '"{}"'.format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))])


	def test(self,  message, callback_id=None, callback_data=None):
		keyboard_reply = self.kb_reply(resize_keyboard = True)
		keyboard_reply.add('домой')
		keyboard_inline = self.kb_inline()
		
		msg = self.edit_message_text(message, 
						  text=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S",))
		self.edit_message_reply(message, 
						  reply_markup = keyboard_reply)
		self.update_mes(msg, update_types = 0)

	def default(self,  message, callback_id=None, callback_data=None):
		keyboard_reply = self.kb_reply(resize_keyboard = True)
		keyboard_reply.add('домой')

		self.send_message(message, 
						  'неактивный раздел\n ' + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S",),
						  keyboard_reply)

#домашняя страница.  home, referal_1
	def home(self, message, callback_id=None, callback_data=None):
		if Database(table_name = 'user_db').select_db('role','where telegram_id = {}'.format(message.chat.id))['result'][0]['role'] == 0:
			self.register_0(message)
		else:
			self.fsm_db(message, 7, 0, 'None')
			keyboard = self.kb_inline()
			#callback_button_time = self.btn_inline(text="сколько времени?",
			#callback_data="6, 1")
			#keyboard.add(callback_button_time)
			
			if Database(table_name = 'user_db').select_db('ref_acc','where telegram_id = {}'.format(message.chat.id))['result'][0]['ref_acc'] == 'None':
					callback_button_ref = self.btn_inline(text="ввести реферальную ссылку", callback_data="9, 10, None")
					keyboard.add(callback_button_ref)
			self.edit_message_text(message=message, 
								   text='домашняя страница\nвремя сервера ' + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S",))
			self.edit_message_reply(message, 
						  reply_markup = keyboard)

			#if message.json['from']['is_bot']:
			#	self.bot.edit_message_text(chat_id=message.chat.id,
			#	message_id=message.message_id,
			#							   text='домашняя страница\nвремя сервера ' +
			#							   datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S",),
			#							   reply_markup=keyboard)
			#else:
			#	self.bot.send_message(chat_id=message.chat.id,
			#							   text='домашняя страница\nвремя сервера ' +
			#							   datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S",),
			#							   reply_markup=keyboard)




	def register(self, message):
		if Database(table_name = 'user_db').select_db('telegram_id','where telegram_id = {}'.format(message.from_user.id))['available'] == 0:
			if len(message.text) > 6:
				ref = message.text[7:]
				print(Database(table_name = 'user_db').select_db('telegram_id','where telegram_id = {}'.format(ref),1))
				if Database(table_name = 'user_db').select_db('telegram_id','where telegram_id = {}'.format(ref))['available'] != 0:
					if Database(table_name = 'user_db').select_db('telegram_id','where telegram_id = {}'.format(ref),1)['result'][0]['telegram_id'] != message.chat.id:
						Database(table_name = 'user_db').update_db('ref_count',
																   'ref_count+1',
																   'where telegram_id = {}'.format(ref))
			else: ref = 'None'
			Database(table_name = 'user_db').insert_db(values = ['{}'.format(message.chat.id),		#telegram_id=
																'"{}"'.format(message.chat.username),	#username
																'"None"',	#pass=
																'"{}"'.format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),#pass_time
																'0',		#pass_count=
																'0',		#role=
																'0',		#dep_status=
																'"0"',		#dep_balance=
																'"0"',		#dept_bet=
																'"{}"'.format(r"https://t.me/bukmekertest_bot?start=" + str(message.chat.id)),#ref_link=
																'"{}"'.format(ref),#ref_acc=
																'0',		#ref_count=
																'"{}"'.format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),#reg_time=
																'"{}"'.format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),#last_mes_time=
																'0',		#last_mes_bot_id=
																'0',		#last_mes_bot_inline_id=
																'0',		#last_mes_user_id=
																'2',		#fsm_code=
																'0',		#fsm_wait=
																'"None"'	#fsm_param=
																])
		self.register_0(message)

	def register_0(self, message, callback_id=None, callback_data=None):
		keyboard_inline = self.kb_inline()
		callback_button_register = self.btn_inline(text="регистрация", callback_data="3, 0, None")
		callback_button_demo = self.btn_inline(text="ДЕМО счёт", callback_data="1, 0, None")
		keyboard_inline.add(callback_button_register, callback_button_demo)
		keyboard_reply = self.kb_reply(resize_keyboard = True)
		keyboard_reply.add('домой','отмена')

		self.send_message(message, 
						  'добро пожаловать в систему!',
						  keyboard_reply)

		msg = self.bot.send_message(chat_id=message.chat.id, 
							  text='хотите открыть основной счёт? \nили потренероваться на ДЕМО счёте?',
							  reply_markup = keyboard_inline)
		Database(table_name = 'user_db').update_db('last_mes_bot_inline_id',
												   '"{}"'.format(msg.message_id),
												   'where telegram_id = {}'.format(message.chat.id))
		self.fsm_db(message, 2, 0, 'None')


	def register_1(self, message, callback_id, callback_data):
		keyboard_inline = self.kb_inline()
		callback_button_register = self.btn_inline(text="создать пароль", callback_data="4, 5, None")
		callback_button_demo = self.btn_inline(text="зарегистрироваться без пароля", callback_data="8, 7, None")
		keyboard_inline.add(callback_button_register, callback_button_demo)
		
		self.edit_message_reply(message, 'для защиты аккаунта рекомендуем вам придумать пароль', keyboard_inline)
		
		self.fsm_db(message, callback_data = callback_data)


	def pass_1(self, message, callback_id, callback_data):
		if callback_data != None:
			
			self.send_message(message, "введите придуманный пароль")
			self.fsm_db(message, callback_data = callback_data)



	def pass_2(self, message, callback_id, callback_data):
		if callback_data == None:
			keyboard_inline = self.kb_inline()
			callback_button = self.btn_inline(text="подтвердить пароль", callback_data="6, 0, {}".format(message.text))
			keyboard_inline.add(callback_button)
			self.edit_message_reply(message, text = 'ваш пароль: {} \nесли всё верно - нажмите кнопку "подтвердить пароль"\nв случае ошибки нажмите "отмена"'.format(message.text), keyboard_inline = keyboard_inline)
			#self.bot.send_message(chat_id=message.chat.id, text='ваш пароль: {} \nесли всё верно - нажмите кнопку "подтвердить пароль"\nв случае ошибки нажмите "отмена"'.format(message.text), reply_markup=keyboard)

			self.fsm_db(message, 5, 0, message.text)
	

	def pass_3(self, message, callback_id, callback_data):
		if callback_data != None:
			data = callback_data.split(', ')
			fsm_code = int(data[0])
			fsm_wait = int(data[1])
			fsm_param = str(data[2])
			if fsm_param != "None":
				self.send_message(message, 'пароль установлен'.format(message.text))
				Database(table_name = 'user_db').update_db('pass',
														   '"{}"'.format(Database(table_name = 'user_db').select_db('*','where telegram_id = {}'.format(message.chat.id))['result'][0]['fsm_param']),
														   'where telegram_id = {}'.format(message.chat.id))
				Database(table_name = 'user_db').update_db('pass_time',
														   '"{}"'.format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")),
														   'where telegram_id = {}'.format(message.chat.id))
			Database(table_name = 'user_db').update_db('role',
													   '1',
													   'where telegram_id = {}'.format(message.chat.id))
			self.fsm_db(message, 6, 0, 'None')
			self.home(message, callback_id, callback_data)


#referal_2
	def referal_1(self, message, callback_id, callback_data):
		self.bot.send_message(chat_id=message.chat.id, text="введите ссылку, присланную вам человеком, пригласившим вас")
		self.fsm_db(message, callback_data = callback_data)


	def referal_2(self, message, callback_id, callback_data):
		if callback_data == None:
			if message.text.find('=') != -1:
				ref = message.text.split('=')[1]
				keyboard = self.kb_inline()
				callback_button = self.btn_inline(text="подтвердить", callback_data="11, 0, {}".format(ref))
				keyboard.add(callback_button)
				user_db = Database(table_name = 'user_db').select_db('*','where telegram_id = {}'.format(message.chat.id))
				if user_db['available'] != 0:
					self.bot.send_message(chat_id=message.chat.id, text='пользователь, рефералом которого вы являетесь: {} \nесли всё верно - нажмите кнопку "подтвердить"\nв случае ошибки нажмите "отмена"'.format(user_db['result'][0]['username']), reply_markup=keyboard)
					self.fsm_db(message, 10, 0, ref)
				else: 
					self.bot.send_message(chat_id=message.chat.id, text='такой пользователь не найден')
					self.home(message, callback_id, callback_data)

#exit point
	def referal_3(self, message, callback_id, callback_data):
		if callback_data != None:
			data = callback_data.split(', ')
			fsm_code = int(data[0])
			fsm_wait = int(data[1])
			fsm_param = str(data[2])
			if fsm_param != "None":
				
				if Database(table_name = 'user_db').select_db('telegram_id','where telegram_id = {}'.format(fsm_param))['available'] != 0:
					if str(fsm_param) != str(message.chat.id):
						if Database(table_name = 'user_db').select_db('ref_acc','where telegram_id = {}'.format(message.chat.id))['result'][0]['ref_acc'] == 'None':
							self.bot.send_message(chat_id=message.chat.id, text='спасибо за участие в партнёрской программе')
							Database(table_name = 'user_db').update_db('ref_count',
																	   'ref_count+1',
																	   'where telegram_id = {}'.format(fsm_param))
							Database(table_name = 'user_db').update_db('ref_acc',
																	   '"{}"'.format(fsm_param),
																	   'where telegram_id = {}'.format(message.chat.id))
							self.fsm_db(message, 11, 0, 'None')
							self.home(message, callback_id, callback_data)
						else:
							self.bot.send_message(chat_id=message.chat.id, text='вы уже были приглашены другим пользователем')
							self.home(message, callback_id, callback_data)
					else:
						self.bot.send_message(chat_id=message.chat.id, text='нельзя стать своим собственным рефералом')
						self.home(message, callback_id, callback_data)
				else:
					self.bot.send_message(chat_id=message.chat.id, text='такой пользователь не найден')
					self.home(message, callback_id, callback_data)
			else:
				self.bot.send_message(chat_id=message.chat.id, text='ошибка ввода')
				self.home(message, callback_id, callback_data)