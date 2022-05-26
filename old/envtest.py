from decouple import config

MONGO_URI = config('MONGO_URI')

print(MONGO_URI)