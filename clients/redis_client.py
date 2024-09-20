from redis import Redis
from os import getenv

class RedisClient(Redis):
    def __init__(self):
        super().__init__(
            host='redis',   # This is the name of the service in the docker-compose file
            port=getenv('REDIS_PORT'),
            decode_responses=True,
            protocol=3
        )