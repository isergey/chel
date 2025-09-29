from django.contrib.auth.signals import user_login_failed
from django.core.cache import cache
from django.conf import settings
from django.dispatch import receiver
import time


@receiver(user_login_failed)
def track_login_failed(sender, credentials, request, **kwargs):
    print('user_login_failed', user_login_failed)
    """
    Обработчик неудачных попыток входа
    """
    username = credentials.get('username')
    ip_address = get_client_ip(request)

    if not username or not ip_address:
        return

    # Ключи для кеша
    ip_key = f'login_failures_ip_{ip_address}'
    user_key = f'login_failures_user_{username}'
    combined_key = f'login_failures_combined_{ip_address}_{username}'

    # Текущее время
    current_time = time.time()

    # Настройки из settings.py или значения по умолчанию
    max_attempts = getattr(settings, 'LOGIN_FAILURE_LIMIT', 10)
    timeout_duration = getattr(settings, 'LOGIN_FAILURE_TIMEOUT', 3600)  # 1 час
    window_duration = getattr(settings, 'LOGIN_FAILURE_WINDOW', 900)  # 15 минут

    # Обновляем счетчики
    update_failure_count(ip_key, max_attempts, window_duration, timeout_duration, current_time)
    update_failure_count(user_key, max_attempts, window_duration, timeout_duration, current_time)
    update_failure_count(combined_key, max_attempts, window_duration, timeout_duration, current_time)


def update_failure_count(key, max_attempts, window_duration, timeout_duration, current_time):
    """
    Обновляет счетчик неудачных попыток и проверяет блокировку
    """
    failures_data = cache.get(key, {'count': 0, 'first_attempt': current_time})

    # Сбрасываем счетчик если окно времени истекло
    if current_time - failures_data['first_attempt'] > window_duration:
        failures_data = {'count': 0, 'first_attempt': current_time}

    # Увеличиваем счетчик
    failures_data['count'] += 1
    failures_data['last_attempt'] = current_time

    # Сохраняем в кеше
    cache.set(key, failures_data, timeout_duration)

    # Логируем событие
    if failures_data['count'] >= max_attempts:
        print(f"Превышен лимит попыток входа для ключа: {key}")


def get_client_ip(request):
    """
    Получает IP адрес клиента
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip