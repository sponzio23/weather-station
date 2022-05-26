from gpiozero import Button

rain_sensor = Button(6)
bucket_size = 0.2794 #mm
count = 0

def bucket_tipped():
    global count
    count = count + 1
    print(count * bucket_size)

def reset_rainfall():
    global count
    count = 0

rain_sensor.when_pressed = bucket_tipped
