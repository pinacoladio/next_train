from datetime import datetime
import psycopg2
import math
import wheel
import telebot

conn = psycopg2.connect(dbname='tg_bot', user='postgres',
                        password='123456', host='localhost',
                        port='5433')
apikey = 'fc81eaca-788e-4315-b254-f08ba6e7ce04'
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
                             "через " + str(info_for_output['minutes']) + " минуту" )
        elif(info_for_output['minutes']%10 in (2,3,4) and info_for_output['minutes'] not in (12,13,14)):
            print_out.append("Следующая электричка (" + info_for_output['type'] + \
                             ") по машруту " + info_for_output['trajectory'] + " будет " \
                             "через " + str(info_for_output['minutes']) + " минуты" )
            # print("Следующая электричка (%(type)s) по машруту %(trajectory)s будет через %(minutes)s минуты" % info_for_output)
        else:
            print_out.append("Следующая электричка (" + info_for_output['type'] + \
                             ") по машруту " + info_for_output['trajectory'] + " будет " \
                             "через " + str(info_for_output['minutes']) + " минут" )
            # print("Следующая электричка (%(type)s) по машруту %(trajectory)s будет через %(minutes)s минут" % info_for_output)
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
#     print(query % info_for_query)
    cursor.execute(query, info_for_query)
    records = cursor.fetchall()
    return printing_answer(records)
	
token = "5483253629:AAE6VKfdJoyy87xd5xVPWMcuW-YQ4-V_xzU"
bot = telebot.TeleBot('5713337542:AAF-fI_hE8wtZArlFuNiP9zCr71y6mz1Rko')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/next_novodachka":
        out = when_next(stations['Новодачная'])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out))
    elif message.text == "/next_savyolovskaya":
        out = when_next(stations['Савёловский вокзал'])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out))    
    elif message.text == "/next_timiryazevskaya":
        out = when_next(stations['Тимирязевская'])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out))    
    elif message.text == "/next_belorusckij":
        out = when_next(stations['Белорусcкий вокзал'])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out))    
    elif message.text == "/next_testovskaya":
        out = when_next(stations['Тестовская'])
        if(len(out) == 0):
            bot.send_message(message.from_user.id, "На сегодня электричек нет")
        else:
            bot.send_message(message.from_user.id, " \n".join(out))  
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю.Доступные команды \n" \
        "/next_novodachka \n" \
        "/next_timiryazevskaya \n" \
        "/next_savyolovskaya \n" \
        "/next_belorusckij \n" \
        "/next_testovskaya \n" \
        )

bot.polling()
