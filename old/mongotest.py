from pymongo import MongoClient
from decouple import config

MONGO_URI = config('MONGO_URI')

client = MongoClient(MONGO_URI)
db = client.PutneyWeather

data = {
    'rainfall' : 1,
    'humidity' : 1,
    'pressure': 1,
    'temp' : 1,
    'wind_speed' : 1,
    'wind_gust' : 1,
    'wind_direction' : 1
}

result = db.weatherData.insert_one(data)

print('inserted data')
