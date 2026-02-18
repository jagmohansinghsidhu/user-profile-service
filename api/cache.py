import os
import json
from functools import wraps

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import redis
from redis.retry import Retry
from redis.exceptions import (TimeoutError, ConnectionError)
from redis.backoff import ExponentialBackoff


class RedisClient:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.redis = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=os.environ.get('REDIS_PORT', 6379),
            db=os.environ.get('REDIS_DB', 0),
            retry=Retry(ExponentialBackoff(cap=10, base=1), 25),
            retry_on_error=[ConnectionError, TimeoutError],
            health_check_interval=1
        )

    def get_key(self, key: str):
        return self.redis.get(key)

    def setex(self, key: str, ttl: int, value: str) -> bool:
        return self.redis.setex(key, ttl, value)


def get_redis_cache():
    return RedisClient()


def cache_response(ttl: int = 60, key_prefix: str = '', params: list[str] | None = None):

    def decorator(handler):
        @wraps(handler)
        def wrapper(*args, **kwargs):
            cache_header = "X-LB-Cache"
            cache_client = RedisClient()
            cache_key = f"{key_prefix}"

            if params:
                key_suffix = ":".join([str(kwargs.get(param)) for param in params])
                cache_key = f"{key_prefix}:{key_suffix}"

            cached = cache_client.get_key(cache_key)

            if cached:

                return JSONResponse(
                    content=json.loads(cached),
                    headers={cache_header: "HIT"}
                )

            response_content = handler(*args, **kwargs)

            content = jsonable_encoder(response_content)
            cache_client.setex(cache_key, ttl, json.dumps(content))

            return response_content

        return wrapper

    return decorator


def update_response_cache(ttl: int = 60, key_prefix: str = '', params: list[str] | None = None):

    def decorator(handler):
        @wraps(handler)
        def wrapper(*args, **kwargs):
            cache_client = RedisClient()
            cache_key = f"{key_prefix}"
            if params:
                key_suffix = ":".join([str(kwargs.get(param)) for param in params])
                cache_key = f"{key_prefix}:{key_suffix}"

            response_content = handler(*args, **kwargs)

            content = jsonable_encoder(response_content)
            print(response_content)
            cache_client.setex(cache_key, ttl, json.dumps(content))

            return response_content
        return wrapper

    return decorator

