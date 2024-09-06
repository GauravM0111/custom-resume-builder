from redis import Redis
from os import getenv

class RedisClient():
    def __init__(self):
        self.client = Redis(
            host='redis',   # This is the name of the service in the docker-compose file
            port=getenv('REDIS_PORT'),
            decode_responses=True,
            protocol=3
        )
    
    def set_data(self, key: str, value: str, expires_in_seconds: int = None) -> None:
        print('Setting data in Redis...')
        print(f"{key} -> {value}")

        if not self.client.set(key, value, ex=expires_in_seconds):
            raise Exception(f'Error setting: {key} -> {value}')
    
    def get_data(self, key: str) -> str:
        print('Getting data from Redis...')
        print(f"{key} -> {self.client.get(key)}")

        return self.client.get(key)