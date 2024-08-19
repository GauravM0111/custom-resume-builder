from flask import Flask
from redis import Redis
import os
from pymongo import MongoClient

app = Flask(__name__)

redis_client = Redis(
    host='redis',   # This is the name of the service in the docker-compose file
    port=os.getenv('REDIS_PORT'),
    decode_responses=True,
    protocol=3
)

mongo_client = MongoClient(
    host='mongo',   # This is the name of the service in the docker-compose file
    port=int(os.getenv('MONGO_PORT')),
)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/set/<key>/<value>', methods=['POST'])
def set(key, value):
    if redis_client.set(key, value):
        return f'{key} set to {value}'
    else:
        return 'Error setting key'

@app.route('/get/<key>', methods=['GET'])
def get(key):
    value = redis_client.get(key)
    return f'{key} is set to {value}'

if __name__ == '__main__':
    app.run()