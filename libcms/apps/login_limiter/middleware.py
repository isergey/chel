import time
from functools import lru_cache

from django.core.cache import cache
from django.http import JsonResponse, HttpRequest
from django.shortcuts import resolve_url

from .config import get_config


@lru_cache
def resolve_login_url():
    return resolve_url('login')

class LoginBlockMiddleware:
    """
    Middleware для блокировки запросов на вход при превышении лимита
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        login_url = resolve_login_url()

        if request.path == login_url and request.method == 'POST':
            username = request.POST.get('username', '')
            ip_address = self.get_client_ip(request)

            if self.is_blocked(ip_address, username):
                return JsonResponse({
                    'error': 'Превышено количество попыток входа. Пожалуйста, попробуйте позже.'
                }, status=429, json_dumps_params={'ensure_ascii': False})

        return self.get_response(request)

    @classmethod
    def is_blocked(cls, ip_address, username):
        """
        Проверяет, заблокирован ли IP или пользователь
        """

        config = get_config()

        keys_to_check = [
            f'login_failures_ip_{ip_address}',
            f'login_failures_user_{username}',
            f'login_failures_combined_{ip_address}_{username}'
        ]

        current_time = time.time()

        for key in keys_to_check:
            failures_data = cache.get(key)
            if failures_data:
                # Проверяем находится ли в пределах временного окна
                if current_time - failures_data['first_attempt'] <= config.window_duration:
                    if failures_data['count'] >= config.max_attempts:
                        return True
                else:
                    # Удаляем устаревшие данные
                    cache.delete(key)

        return False

    @classmethod
    def get_client_ip(cls, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip