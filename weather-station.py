from gpiozero import Button
from gpiozero import MCP3008
import bme280
import smbus2
import time
import statistics
import math
from pymongo import MongoClient
from decouple import config

interval = 30
wind_interval = 5

# Database things
MONGO_URI = config('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client.PutneyWeather
print("Connected to the database!")

# Rain things
rain_sensor = Button(6)
bucket_size = 0.2794 #mm
rain_count = 0

def bucket_tipped():
    global rain_count
    rain_count = rain_count + 1

def reset_rainfall():
    global rain_count
    rain_count = 0

rain_sensor.when_pressed = bucket_tipped

# bme280 things
port = 1
address = 0x77
bus = smbus2.SMBus(port)
bme280.load_calibration_params(bus,address)

def read_bme280():
    global bus
    global address
    bme280_data = bme280.sample(bus, address)
    return bme280_data.humidity, bme280_data.pressure, bme280_data.temperature

# Wind speed things
store_speeds = []

wind_count = 0
radius_cm = 9.0
adjustment = 1.18

cm_in_a_km = 100000.0
secs_in_an_hour = 3600

def spin():
    global wind_count
    wind_count = wind_count + 1

def calculate_speed(time_sec):
    global wind_count
    circumference_cm = (2*math.pi) * radius_cm
    rotations = wind_count / 2.0

    # Calculate distance travelled by a cup in cm
    dist_km = (circumference_cm * rotations) / cm_in_a_km
    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * secs_in_an_hour
    
    return km_per_hour * adjustment

def reset_wind():
    global wind_count
    wind_count = 0

wind_speed_sensor = Button(5)
wind_speed_sensor.when_pressed = spin

# Wind direction things
adc = MCP3008(channel=0)
store_directions = []

volts = {0.4: 0.0,
         1.4: 22.5,
         1.2: 45.0,
         2.8: 67.5,
         2.7: 90.0,
         2.9: 112.5,
         2.2: 135.0,
         2.3: 1000000,
         2.5: 157.5,
         1.8: 180.0,
         2.0: 202.5,
         0.7: 225.0,
         0.8: 247.5,
         0.1: 270.0,
         0.3: 292.5,
         0.2: 315.0,
         0.6: 337.5}

def get_average(angles):
    sin_sum = 0.0
    cos_sum = 0.0
    
    for angle in angles:
        r = math.radians(angle)
        sin_sum += math.sin(r)
        cos_sum += math.cos(r)

        flen = float(len(angles))
        s = sin_sum / flen
        c = cos_sum / flen
        arc = math.degrees(math.atan(s / c))
        average = 0.0

        if s > 0 and c > 0:
            average = arc
        elif c < 0:
            average = arc + 180
        elif s < 0 and c > 0:
            average = arc + 360

        return 0.0 if average == 360 else average



while True:
    start_time = time.time()
    while time.time() - start_time <= interval:
        reset_wind()
        
        wind_start_time = time.time()
        while time.time() - wind_start_time <= wind_interval:
            wind = round(adc.value*3.3,1)
            if not wind in volts:
                useless = 1+1
            else:
                store_directions.append(volts[wind])
        
        final_speed = calculate_speed(wind_interval)
        store_speeds.append(final_speed)
    
    # Define things that are wind
    wind_gust = max(store_speeds)
    wind_speed = statistics.mean(store_speeds)
    
    wind_direction = get_average(store_directions)


    # Define things that aren't wind
    rainfall = rain_count * bucket_size
    humidity, pressure, temp = read_bme280()

    # Print things
    print(rainfall)
    print(humidity, pressure, temp)
    print(wind_speed, wind_gust)
    print (wind_direction)

    # Insert things into the database
    data = {
        'rainfall' : rainfall,
        'humidity' : humidity,
        'pressure': pressure,
        'temp' : temp,
        'wind_speed' : wind_speed,
        'wind_gust' : wind_gust,
        'wind_direction' : wind_direction
    }
    
    result = db.weatherData.insert_one(data)
    print('inserted data')

    # Reset things
    store_speeds = []
    reset_rainfall()
    store_directions = []
