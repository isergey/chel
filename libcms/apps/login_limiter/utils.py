from django.core.cache import cache
from django.contrib.auth.signals import user_logged_in


def reset_login_failures(username=None, ip_address=None):
    """
    Сбрасывает счетчики неудачных попыток входа
    """
    keys_to_delete = []

    if username:
        keys_to_delete.append(f'login_failures_user_{username}')

    if ip_address:
        keys_to_delete.append(f'login_failures_ip_{ip_address}')

    if username and ip_address:
        keys_to_delete.append(f'login_failures_combined_{ip_address}_{username}')

    for key in keys_to_delete:
        cache.delete(key)


def get_login_attempts_count(username=None, ip_address=None):
    """
    Возвращает количество оставшихся попыток
    """
    max_attempts = 5  # Значение по умолчанию

    if username and ip_address:
        key = f'login_failures_combined_{ip_address}_{username}'
    elif username:
        key = f'login_failures_user_{username}'
    elif ip_address:
        key = f'login_failures_ip_{ip_address}'
    else:
        return max_attempts

    failures_data = cache.get(key, {'count': 0})
    remaining = max(0, max_attempts - failures_data['count'])
    return remaining


def login_success_handler(sender, request, user, **kwargs):
    """
    Обработчик успешного входа - сбрасывает счетчики
    """
    ip_address = get_client_ip(request)
    reset_login_failures(username=user.username, ip_address=ip_address)


# Подключаем сигнал успешного входа
user_logged_in.connect(login_success_handler)


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