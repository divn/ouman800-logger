import requests
import time
import os
import mysql.connector
import config

# Database config
dbconfig = config.DBCONFIG

# Ip and port of OUMAN EH800, CHANGE THIS
ip = config.OUMANIP
# Wanted measurepoints. More from sourcecode of OUMANEH800 webinterface
measures = ['S_272_85', 'S_261_85', 'S_259_85', 'S_227_85']
# Measurepoint names handwritten in right order
names = ['Venttiilin asento', 'Sisälämpötila', 'Menoveden Lämpötila',
         'Ulkolämpötila']

while True:
    try:
        # Fetch wanted temperatures from OUMAN,
        temp = requests.get('http://' + ip + '/request?' + ';'.join(measures),
                            timeout=1)
        timenow = time.strftime('%Y-%m-%d %H:%M:%S')
        data = temp.text

        # Data starts with request? strip it from string
        if data.startswith('request?'):
            data = data[8:-4]

        # Convert String into list
        data = data.split(';')

        # Store values that will be send to database
        data_values = (timenow, float(data[0][9:]), float(data[1][9:]),
                       float(data[2][9:]), float(data[3][9:]))

        # Print value and equilevant name
        print('=' * 10 + timenow + '=' * 10)
        for name, data in zip(names, data):
            print('{:20}'.format(name) + ' ' + data[9:])

        print('OUMAN OK!')

    # if theres no connection to OUMAN print this error msg
    except requests.exceptions.RequestException:
        print('OUMAN ERROR')

    # Database connection and inserting values
    try:
        connection = mysql.connector.connect(**dbconfig)
        cursor = connection.cursor()

        add_values = ('INSERT INTO log'
                      '(TIME, VENTTIILI, SISLAMPO, VESILAMPO, ULKLAMPO)'
                      'VALUES (%s, %s, %s, %s, %s )')

        cursor.execute(add_values, data_values)
        connection.commit()

        cursor.close()
        connection.close()
        print('DATABASE OK!')

    except mysql.connector.Error:
        print('DATABASE ERROR')

    # Sleep for Seconds start over
    time.sleep(30)
    os.system('cls||clear')
