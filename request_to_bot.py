from datetime import datetime
from telebot import types
import psycopg2
import math
import wheel
import telebot
import random
import os


class Cat_picture:
    
    cat_picture = open('cats/' + random.choice(os.listdir('cats')), 'rb')
    
    def get_picture_random(n):
        if random(0,1):
            return cat_picture
        else:
            pass     

with open("secret_info.txt", "r") as file:
    data_array = file.readlines()
    data_struct = [item.split() for item in data_array]
    secret_dict = {item[0]:item[1] for item in data_struct}
    
conn = psycopg2.connect(dbname = secret_dict['dbname'], 
                        user = secret_dict['user'],
                        password = secret_dict['password'], 
                        host = secret_dict['host'],
                        port = secret_dict['port'])

cursor = conn.cursor()
conn.autocommit = True
bot = telebot.TeleBot(secret_dict['bot'])

def cat_picture() :
    name_jpg = 'cats/1.jpg'
    return name_jpg

def printing_answer(records):
    print_out = []
    for row in records:
        info_for_output = {
            'minutes': math.ceil(row[1]/60),
            'trajectory': row[2],
            'type': row[3]
        }
        if(info_for_output['minutes']%10 == 1 and info_for_output['minutes'] != 11):
            print_out.append("Следующая электричка (" + info_for_output['type'] + \
                             ") по машруту *" + info_for_output['trajectory'] + "* будет " \
                             "через *" + str(info_for_output['minutes']) + "* минуту" )
        elif(info_for_output['minutes']%10 in (2,3,4) and info_for_output['minutes'] not in (12,13,14)):
            print_out.append("Следующая электричка (" + info_for_output['type'] + \
                             ") по машруту *" + info_for_output['trajectory'] + "* будет " \
                             "через *" + str(info_for_output['minutes']) + "* минуты" )
        else:
            print_out.append("Следующая электричка (" + info_for_output['type'] + \
                             ") по машруту *" + info_for_output['trajectory'] + "* будет " \
                             "через *" + str(info_for_output['minutes']) + "* минут" )
    return print_out

stations = {
    '/next_novodachka' : 's9601261', 
    '/next_okruzhnaya' :  's9601830', 
    '/next_timiryazevskaya' : 's9602463', 
    '/next_savyolovskaya' : 's2000009', 
    '/next_belorusckij' : 's2000006', 
    '/next_testovskaya' : 's9601349', 
    'Новодачная' : 's9601261', 
    'Окружная' : 's9601830', 
    'Тимирязевская' : 's9602463', 
    'Савёловский вокзал' : 's2000009', 
    'Белорусcкий вокзал' :  's2000006', 
    'Тестовская' :  's9601349' 
}

def when_next(station):
    ts_now = round(datetime.now().timestamp())
    info_for_query = {
        'ts_now' : ts_now,
        'station' : station
        }
    if station == stations['Новодачная'][0]:
            query = 'SELECT timestamp_arrival, MAX(timestamp_arrival -  %(ts_now)s), MAX(thread), MAX(type) \n'\
                    'FROM data \n' \
                    "WHERE direction IN ('на Москву','Белорусское направление') and timestamp_arrival > %(ts_now)s and station = %(station)s  \n"\
                    'GROUP BY timestamp_arrival \n'\
                    'ORDER BY timestamp_arrival \n'\
                    'LIMIT 3'  
    else:
            query = 'SELECT timestamp_arrival, MAX(timestamp_arrival -  %(ts_now)s), MAX(thread), MAX(type) \n'\
                    'FROM data \n' \
                    "WHERE direction NOT IN ('на Москву','Белорусское направление','прибытие') and timestamp_arrival > %(ts_now)s and station = %(station)s  \n"\
                    'GROUP BY timestamp_arrival \n'\
                    'ORDER BY timestamp_arrival \n'\
                    'LIMIT 3'  
    cursor.execute(query, info_for_query)
    records = cursor.fetchall()
    return printing_answer(records)

@bot.message_handler(commands=['start'])
def first_message(message):
    mes = bot.send_message(message.from_user.id, "Привет! Я бот, который говорит сколько времени до прибытия электрички.\n "\
    "Сейчас соориентирую тебя немного в соём функционале.\n"\
    "Я подсказфваю время прибытия электричек по таким путям: \n"\
    "Новодачная на Москву -> команда Новодачная или /next_novodachka \n" \
    "Окружная на Новодачную -> команда Окружная или /next_okruzhnaya \n" \
    "Тимирязевская на Новодачную -> команда Тимирязевская или /next_timiryazevskaya \n" \
    "Савёловский вокзал на Новодачную  -> команда Савёловский вокзал или /next_savyolovskaya \n" \
    "Белорусcкий вокзал на Новодачную -> команда Белорусcкий вокзал или /next_belorusckij \n" \
    "Тестовская на Новодачную -> команда Тестовская или /next_testovskaya \n" \
    "Так же если что пиши команду /help она снова подскажет направление электричек и их команды. У меня есть меню с кнопочками, для быстроты активно используй их))")

@bot.message_handler(commands=['help'])
def help_message(message):
    mes = bot.send_message(message.from_user.id, "Снова привет! вот подсказка если что-то подзабыл или неправильно написал: \n" \
    "Новодачная на Москву -> команда Новодачная или /next_novodachka \n" \
    "Окружная на Новодачную -> команда Окружная или /next_okruzhnaya \n" \
    "Тимирязевская на Новодачную -> команда Тимирязевская или /next_timiryazevskaya \n" \
    "Савёловский вокзал на Новодачную  -> команда Савёловский вокзал или /next_savyolovskaya \n" \
    "Белорусcкий вокзал на Новодачную -> команда Белорусcкий вокзал или /next_belorusckij \n" \
    "Тестовская на Новодачную -> команда Тестовская или /next_testovskaya \n" \
    "Так же если что пиши команду /help она снова подскажет направление электричек и их команды. У меня есть меню с кнопочками, для быстроты активно используй и их)")
                           
@bot.message_handler(commands=['menu'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    for key in stations.keys() :
        if (key[0] != '/') :
            button = types.KeyboardButton(key)
            markup.add(button)
                
    bot.send_message(message.chat.id,'Выберите c какой станции вы отбываете среди кнопок меню',reply_markup=markup)
    
    
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text in stations.keys() :
        out = when_next(stations[message.text])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out), parse_mode = "Markdown")
            bot.send_photo(message.from_user.id, photo = open(cat_picture(), 'rb')) 
    else:
        bot.send_message(message.from_user.id, "Извини я тебя не понимаю, пожалуйста проверь написание команд" \
                         "Если что можешь вызвать команду /help или меню" )


bot.polling(none_stop=True, interval=0)
