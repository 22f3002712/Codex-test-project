import redis
from flask import current_app


def get_redis_client():
    return redis.Redis.from_url(current_app.config["REDIS_URL"])
