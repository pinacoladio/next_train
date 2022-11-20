from datetime import datetime
import psycopg2
import math
import wheel
import telebot
from telebot import types

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
                             ") по машруту " + info_for_output['trajectory'] + " будет " \
                             "через *" + str(info_for_output['minutes']) + "* минуту" )
        elif(info_for_output['minutes']%10 in (2,3,4) and info_for_output['minutes'] not in (12,13,14)):
            print_out.append("Следующая электричка (" + info_for_output['type'] + \
                             ") по машруту " + info_for_output['trajectory'] + " будет " \
                             "через *" + str(info_for_output['minutes']) + "* минуты" )
        else:
            print_out.append("Следующая электричка (" + info_for_output['type'] + \
                             ") по машруту " + info_for_output['trajectory'] + " будет " \
                             "через *" + str(info_for_output['minutes']) + "* минут" )
    return print_out

stations = {
    'Новодачная' : 's9601261', 
    'Окружная' : 's9855182',
    'Тимирязевская' : 's9602463',
    'Савёловский вокзал' : 's2000009',
    'Белорусcкий вокзал' : 's2000006',
    'Тестовская' : 's9601349',
}

def when_next(station):
    ts_now = round(datetime.now().timestamp())
    info_for_query = {
        'ts_now' : ts_now,
        'station' : station
        }
    if station == stations['Новодачная']:
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
	
bot = telebot.TeleBot(secret_dict['bot'])

# Еще я бы сделала акценты в тексте который мы выводим, я нашла вариант с классом который делает текст вывода 
#цветным или просто с жирным текстом 
#class style:
#   BOLD = '\033[1m'
#   END = '\033[0m'
#   PURPLE = '\033[95m'
#   CYAN = '\033[96m'
#print(color.BOLD + 'Hello, World!' + color.END)
# как тебе идея?

@bot.message_handler(commands=['start'])
def first_message(message):
    mes = bot.send_message(message.from_user.id, "Привет! Я бот, который говорит сколько времени до прибытия электрички.\n "\
    "Сейчас соориентирую тебя немного в соём функционале.\n"\
    "Я подсказфваю время прибытия электричек по таким путям: \n"\
    "Новодачная на Москву -> команда Новодачная или /next_novodachka \n "\
    "Савёловский вокзал на ... -> команда Савёловский вокзал или /next_savyolovskaya \n "\
    "Тимирязевская на ... -> команда Тимирязевская или /next_timiryazevskaya \n "\
    "Белорусcкий вокзал на ... -> команда Белорусcкий вокзал или /next_belorusckij \n" \
    "Тестовская на ... -> команда Тестовская или /next_testovskaya \n" \
    "Так же если что пиши команду /help она снова подскажет направление электричек и их команды. У меня есть меню с кнопочками, для быстроты активно используй их))")

@bot.message_handler(commands=['help'])
def help_message(message):
    mes = bot.send_message(message.from_user.id, "Снова привет! вот подсказка если что-то подзабыл или неправильно написал: \n" \
    "Новодачная на Москву -> команда Новодачная или /next_novodachka \n" \
    "Савёловский вокзал на ... -> команда Савёловский вокзал или /next_savyolovskaya \n" \
    "Тимирязевская на ... -> команда Тимирязевская или /next_timiryazevskaya \n" \
    "Белорусcкий вокзал на ... -> команда Белорусcкий вокзал или /next_belorusckij \n" \
    "Тестовская на ... -> команда Тестовская или /next_testovskaya \n" \
    "Так же если что пиши команду /help она снова подскажет направление электричек и их команды. У меня есть меню с кнопочками, для быстроты активно используй и их)")
                           
@bot.message_handler(commands=['menu'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    button1 = types.KeyboardButton("Новодачная")
    markup.add(button1)
    
    button2 = types.KeyboardButton('Савёловский вокзал')
    markup.add(button2)
    
    button3 = types.KeyboardButton('Тимирязевская')
    markup.add(button3)
    
    button4 = types.KeyboardButton('Белорусcкий вокзал')
    markup.add(button4)
    
    button5 = types.KeyboardButton('Тестовская')
    markup.add(button5)
    
    bot.send_message(message.chat.id,'Выберите c какой станции вы отбываете среди кнопок меню',reply_markup=markup)
    
    
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text in ("Новодачная", "/next_novodachka"):
        out = when_next(stations['Новодачная'])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out))
    elif message.text in ("Савёловский вокзал", "/next_savyolovskaya"):
        out = when_next(stations['Савёловский вокзал'])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out))    
    elif message.text in ("Тимирязевская", "/next_timiryazevskaya"):
        out = when_next(stations['Тимирязевская'])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out))    
    elif message.text in ("Белорусcкий вокзал", "/next_belorusckij"):
        out = when_next(stations['Белорусcкий вокзал'])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out))    
    elif message.text in ("Тестовская", "/next_testovskaya"):
        out = when_next(stations['Тестовская'])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out), parse_mode = "Markdown")
        if(True):
            bot.send_photo(message.from_user.id, photo=open('cats/1.jpg', 'rb'))
    else:
        bot.send_message(message.from_user.id, "Извини я тебя не понимаю, пожалуйста проверь написание команд. Если что можешь вызвать команду /help или меню" )

bot.polling(none_stop=True, interval=0)
