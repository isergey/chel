from dataclasses import dataclass
from functools import lru_cache

from django.conf import settings


@dataclass
class Config:
    max_attempts: int
    window_duration: int
    timeout_duration: int

    @staticmethod
    def from_django_settings():
        return Config(
            max_attempts=getattr(settings, 'LOGIN_FAILURE_LIMIT', 10),
            window_duration=getattr(settings, 'LOGIN_FAILURE_WINDOW', 900),
            timeout_duration=getattr(settings, 'LOGIN_FAILURE_TIMEOUT', 3600),
        )


@lru_cache
def get_config():
    return Config.from_django_settings()