from gpiozero import Button
import time
import math
import wind_direction
import statistics
import bme280_sensor
#import database

wind_count = 0   # Counts how many half-rotations
radius_cm = 9.0   # Radius of your aneometer
wind_interval = 5   # How often (secs) to report speed
interval = 5 # how often (secs) to sample speed
cm_in_a_km = 100000.0
secs_in_an_hour = 3600
adjustment = 1.18   # Aneometer factor
bucket_size = 0.2794 #mm
rain_count = 0
gust = 0
store_speeds = []
store_directions = []


def spin():
    global wind_count
    wind_count = wind_count + 1
    print(wind_count)

def calculate_speed(time_sec):
    global wind_count
    global gust
    circumference_cm = (2*math.pi) * radius_cm
    rotations = wind_count / 2.0

    dist_km = (circumference_cm * rotations) / cm_in_a_km

    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * secs_in_an_hour

    final_speed = km_per_hour * adjustment

    return final_speed

def bucket_tipped():
    global rain_count
    rain_count = rain_count + 1
    print(rain_count * bucket_size)

def reset_rainfall():
    global rain_count
    rain_count = 0

def reset_wind():
    global wind_count
    wind_count = 0

def reset_gust():
    global gust
    gust = 0

wind_speed_sensor = Button(5)
wind_speed_sensor.when_activated = spin
temp_probe = ds18b20_therm.DS18B20()

#db = database.weather_database()

while True:
    start_time = time.time()
    while time.time() - start_time <= interval:
        wind_start_time = time.time()
        reset_wind()
        #time.sleep(wind_interval)
        while time.time() - wind_start_time <= wind_interval:
            store_directions.append(wind_direction.get_value())
            
        final_speed = calculate_speed(wind_interval)
        store_speeds.append(final_speed)

    wind_average = wind_direction.get_average(store_directions)
    wind_gust = max(store_speeds)
    wind_speed = statistics.mean(store_speeds)
    rainfall = rain_count * bucket_size
    
    ground_temp = temp_probe.read_temp()
    humidity, pressure, ambient_temp = bme280_sensor.read_all()

    print(wind_speed, wind_gust, rainfall, wind_average, humidity, pressure, ambient_temp, ground_temp)
    #db.insert(ambient_temp, ground_temp, 0, pressure, humidity, wind_average, wind_speed, wind_gust, rainfall)

    reset_rainfall()
    store_speeds = []
    store_directions = []
