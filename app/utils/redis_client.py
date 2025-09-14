import redis
import os
from dotenv import load_dotenv

load_dotenv()


class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Read host and port from environment variables
            redis_host = os.environ.get("REDIS_HOST", "localhost")
            redis_port = int(os.environ.get("REDIS_PORT", 6379))
            redis_url = os.environ.get("REDIS_URL")

            if not redis_url:
                cls._instance = redis.Redis(host=redis_host, port=redis_port, db=0)
            else:
                cls._instance = redis.from_url(redis_url)
        return cls._instance
