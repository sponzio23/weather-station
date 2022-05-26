import statistics
from gpiozero import Button
import time
import math

store_speeds = []

wind_count = 0   # Counts how many half-rotations
radius_cm = 9.0   # Radius of your aneometer
wind_interval = 5   # How often (secs) to report speed
adjustment = 1.18   # Aneometer factor

# Defines units
cm_in_a_km = 100000.0
secs_in_an_hour = 3600

# Every half-rotation, add 1 to count 
def spin():
    global wind_count
    wind_count = wind_count + 1
#    print("spin" + str(wind_count))

# Calculate the wind speed
def calculate_speed(time_sec):
    global wind_count
    circumference_cm = (2*math.pi) * radius_cm
    rotations = wind_count / 2.0

    # Calculate distance travelled by a cup in cm
    dist_km = (circumference_cm * rotations) / cm_in_a_km
    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * secs_in_an_hour
    
    return km_per_hour * adjustment

# Resets the wind count
def reset_wind():
    global wind_count
    wind_count = 0

wind_speed_sensor = Button(5)
wind_speed_sensor.when_pressed = spin

# Loop to measure wind speed and report at 5-second intervals
while True:
    start_time = time.time()
    while time.time() - start_time <= wind_interval:
        reset_wind()
        time.sleep(wind_interval)
        final_speed = calculate_speed(wind_interval) # Add this speed to the list
        store_speeds.append(final_speed)
    wind_gust = max(store_speeds)
    wind_speed = statistics.mean(store_speeds)
    print(wind_speed, wind_gust)
