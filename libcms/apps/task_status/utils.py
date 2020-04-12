from django.core.cache import cache
import json
from functools import wraps

KEY_PREFIX = 'task_status'
STORE_TIMEOUT = 60 * 60


def _get_key(name):
    return '{prefix}:{name}'.format(prefix=KEY_PREFIX, name=name)


def task_status(name):
    def real_decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):
            key = _get_key(name)
            value = json.dumps({'status': 'started'}, ensure_ascii=False)
            cache.set(key, value, STORE_TIMEOUT)
            try:
                function(*args, **kwargs)
                cache.delete(key)
            except Exception as e:
                value = json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False)
                cache.set(key, value, STORE_TIMEOUT)
                print(e)
                raise e

        return wrapper

    return real_decorator


def get_task_status(name):
    key = _get_key(name)
    value = cache.get(key)
    print('name', name)
    print('value', value)
    if value is None:
        return {}
    return json.loads(value)
