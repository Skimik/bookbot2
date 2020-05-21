

import pymysql

class Database:
    ''' этот комментарий не совсем соответствует действительности. в действительности же я когда-то его перепишу и он будет ей соответствовать
        а пока, я, читающий свои же модуле после суток в визуалке и ничегошеньки не понимающий, возьми листочек, ручечку, выпиши задачи, идеи, таски                                                                               и пездуй спать, заебал
        и довольствуйся той действительностью, которая сама себе несоответствует

        класс содержит методы для работы с базой данных. полностью (в заданных рамках) настраивается (переписывается)
        описание методов:
        insert принимает на вход название_таблицы и значения в [values]. вставляет [values] в название_таблицы
        select ищет заданный столбец по заданному условию и выводит заданное количество результатов
        update обновляет заданное значение в заданном столбце по заданному условию
        delete удаляет запись из заданной таблицы по условию наличия в ней некоторых ячеек
        executor выполняет код, переданный в параметр sql. если тебе вдруг мало

    '''

    def __init__(self,
                    table_name,
                    database_host = '127.0.0.1',
                    database_user = 'bot_user',
                    database_pass = '123',
                    database_name = 'bot'
                    ):
        '''
        self.database_user = database_user
        self.database_pass = database_pass
        self.database_name = database_name
        '''
        self.table_name = table_name
        self.connection = pymysql.connect(host      =database_host,
                                          user      =database_user,
                                          password  =database_pass,
                                          db        =database_name,
                                          charset   ='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)
#-------------------------------------------------------------------------------
    def insert_db(self, values=[]):
        #вставка значения в базу данных.
        ms_cursor=self.connection.cursor()
        #try:
        sql = "INSERT INTO {} VALUES ({});"
        ms_cursor.execute(sql.format(self.table_name, ', '.join(values)))
        self.connection.commit()
        self.connection.close()
        text = ''
        #except:
            #self.connection.close()
            #text = '--------------------------------------ошибка в функции insert_db'
            #print(text)

#-------------------------------------------------------------------------------
    def select_db(self, searched_column = 'id', condition = '', count_value = 0):
        #поиск наименования в таблице. выводит наличие элемента и результат поиска

        text = ''
        ms_cursor=self.connection.cursor()
        try:
            sql = "select {} from {} {};"
            available=ms_cursor.execute(sql.format( searched_column,
                                                    self.table_name,
                                                    condition))
            if count_value == 0:
                result=ms_cursor.fetchall()
            elif count_value >= 1:
                result=ms_cursor.fetchmany(count_value)
            else: print('ты совсем дурак? в select_db не может быть отрицательного вывода')
            self.connection.commit()
            self.connection.close()
            output={'available':available, 'result':result}
            text = 'у меня всё окей'
        except:
            self.connection.close()
            text = '--------------------------------------ошибка в функции select_db'
            output={'available':None, 'result':None}
            print(text)
        return output

#-------------------------------------------------------------------------------
    def update_db(self, updated_column = 'id', updated_value = 'id', condition = ''):
        #обновление значений в базе данных по заданному условию
        text = ''
        ms_cursor=self.connection.cursor()
        try:
            sql = "update {} set {} = {} {};"
            ms_cursor.execute(sql.format(self.table_name,
                                         updated_column,
                                         updated_value,
                                         condition))
            self.connection.commit()
            self.connection.close()
            text = 'есть проникновение'
            print(text)
        except Exception as ex:
            self.connection.close()
            text = '--------------------------------------ошибка в функции update_db'
            print(text+'\n'+str(ex))

    def delete_db(self, condition = ''):
        #удаление элементов базы данных

        text = ''
        ms_cursor=self.connection.cursor()
        try:
            # Create a new record
            sql = "delete from {} {};"
            ms_cursor.execute(sql.format(self.table_name,
                                         condition))
            self.connection.commit()
            self.connection.close()
            text = 'у меня всё окей'
        except:
            self.connection.close()
            text = '--------------------------------------ошибка в функции delete_db'
            print(text)

#-------------------------------------------------------------------------------
    def executor_db(self, sql):
        #универсальная функция обращения к базе данных. выполняет переданные ей команды в формате sql запросов
        ms_cursor=self.connection.cursor()
        ms_cursor.execute(sql)
        if sql.split(' ')[0].lower() == 'select':
            output = ms_cursor.fetchall()
        else:
            output = 'выхода нет или не найден'
        self.connection.commit()
        self.connection.close()
        return output













#-------------------------------------------------------------------------------
'''
    def select_mdb_all():
        #поиск наименования в таблице. выводит наличие элемента и результат поиска
        connection = pymysql.connect(host='kambot.mysql.pythonanywhere-services.com',
                                     user='kambot',
                                     password='rfvxfnrf',
                                     db='kambot$message_database',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        text = ''
        ms_cursor=connection.cursor()
        try:
            # Create a new record
            sql = "select id from kamusers;"
            available=ms_cursor.execute(sql)
            result=ms_cursor.fetchall()
            connection.commit()
            connection.close()
            output={'available':available, 'result':result}
            text = 'у меня всё окей22'


        except:
            connection.close()
            text = 'ошибка в функции select_mdb_all'
            output={'available':'None', 'result':'None'}

            print(text)

        return output'''
#-------------------------------------------------------------------------------
'''
    def insert_handler(id):
        #проверяем наличие записи в базе данных и вставляем новый айдишник при её отсутствии
        try:

            if select_mdb(id)['available'] == 0:
                print(select_mdb_all()['result'])
                if select_mdb_all()['result']== None:
                    insert_mdb(id, 0, 0)
                    output='запись успешно создана для пользователя:'
                elif len(select_mdb_all()['result']) <= 6:
                    insert_mdb(id, 0, 0)
                    output='запись успешно создана для пользователя:'
                else:
                    output='опоздун:'
            else:
                output='запись уже имеется:'
        except:
            output='ошибка при создании записи:'
        return output'''

'''
    def message_listener(id):
        #заготовка под что то бОльшее. тут должны быть все обработчики сообщений
        text = insert_handler(id)
        return text'''
#-------------------------------------------------------------------------------