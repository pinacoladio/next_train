import time
from datetime import datetime
import requests
import psycopg2
import pprint


with open("secret_info.txt", "r") as file:
    data_array = file.readlines()
    data_struct = [item.split() for item in data_array]
    secret_dict = {item[0]:item[1] for item in data_struct}
    
conn = psycopg2.connect(dbname = secret_dict['dbname'], 
                        user = secret_dict['user'],
                        password = secret_dict['password'], 
                        host = secret_dict['host'],
                        port = secret_dict['port'])

apikey = secret_dict['apikey']
cursor = conn.cursor()
conn.autocommit = True


def make_timestamp(time_string):
    dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S+03:00")
    dt_timestamp = round(dt.timestamp())
    return dt_timestamp


def truncate_data():
    query = 'TRUNCATE data;'
    cursor.execute(query)


def insert_new_line(data):
    query = 'INSERT INTO data (id, timestamp_arrival, station, direction, stops, thread, type) ' \
            'VALUES (%s, %s, %s, %s, %s, %s, %s);'
    cursor.execute(query, data)


def request_api(date_request, station):
    response = requests.get(
        'https://api.rasp.yandex.net/v3.0/schedule/?' +
        'apikey=' + apikey +
        '&station=' + station +
        '&transport_types=' + 'suburban' +
        '&date=' + date_request +
        '&limit=600'
    )
    return response.json()['schedule']


def update_data(date_request, stations_id):
    truncate_data()
    j=0
    for station in stations_id:
        request_data = request_api(date_request, station)
        try:
            for i in range(len(request_data)):
                j += 1
                item = (j,
                    make_timestamp(request_data[i]['arrival'] or request_data[i]['departure']),
                    station,
                    request_data[i]['direction'],
                    request_data[i]['stops'],
                    request_data[i]['thread']['title'],
                    request_data[i]['thread']['transport_subtype']['title']
                    )
                insert_new_line(item)
        except:
            pass
        
        
stations = {
    'Новодачная' : 's9601261', 
    'Окружная' : 's9855182',
    'Тимирязевская' : 's9602463',
    'Савёловский вокзал' : 's2000009',
    'Беллоруский вокзал' : 's2000006',
    'Тестовская' : 's9601349',
}

stations_id = list(stations.values()) 

j=1
while True:
    datetime_now = datetime.now()
    if 0 == datetime_now.hour % 2 or j==1:
        j=0
        today = datetime_now.strftime("%Y-%m-%d")
        print('updating starts, day for update:', today)
        update_data(today, stations_id)
        print('success updating')
        time.sleep(3600*2-500)
