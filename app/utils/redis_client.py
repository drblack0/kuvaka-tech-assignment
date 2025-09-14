import redis


class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = redis.Redis(host="localhost", port=6379, db=0)
        return cls._instance

