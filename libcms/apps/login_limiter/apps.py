from django.apps import AppConfig


class LoginLimiterConfig(AppConfig):
    name = 'login_limiter'

    def ready(self):
        from . import signals
        from . import utils
