from clients.redis_client import RedisClient

class SessionService():
    def __init__(self):
        self.redis = RedisClient()
    
    def create_session(self):
        return None