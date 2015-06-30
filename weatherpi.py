#!/usr/bin/env python

import json
import threading
import time
import logging 
import os
import Adafruit_DHT     # From https://github.com/adafruit/Adafruit_Python_DHT
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer

# Config
PORT = 8080
REFRESH_INTERVAL = 60       # how often to fetch data from the sensors (seconds)
STATIC_DIR = '/static'      # relative path for static content like index.html etc.
LOCATION = 'Home'           # weather location
SENSOR = Adafruit_DHT.DHT22 # use the Adafruit_DHT module
PIN = 4                     # data pin for DHT-22; BCM numbering

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] (%(threadName)-10s) %(message)s')

# Set CWD for static files
os.chdir(os.getcwd() + STATIC_DIR)

# Global weather data object
data = {
        'place': LOCATION,
        'temperature': {'value': '-', 'units': 'F'},
        'humidity': '-'
}

def CtoF(c):
    """Convert temperature in C to F"""
    return c * 1.8 + 32

def fetch_weather():
    """Updates the global weather data object periodically by fetching from the
    sensor"""

    global data
    while True:
        logging.debug('Fetching weather')
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)
        if humidity != None and temperature != None:
            temperature = round(CtoF(temperature), 1)
            humidity = round(humidity, 1)
            data['temperature']['value'] = temperature
            data['temperature']['units'] = 'F'
            data['humidity'] = humidity
            logging.info('Temperature = {0}F  Humidity = {1}%'.format(temperature, humidity))
        else:
            logging.error('Failed to read from sensor')

        time.sleep(REFRESH_INTERVAL)

class WeatherHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        global data
        if self.path.endswith('/api'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            json.dump(data, self.wfile)
            return

        # Delegate to parent class for static content
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':

    # Fork off a thread to fetch the weather at regular intervals
    t = threading.Thread(target = fetch_weather)
    t.daemon = True
    t.start()

    # Serve http
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, WeatherHandler)
    logging.info('Server running at ' + `server_address`)
    httpd.serve_forever()
