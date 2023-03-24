from django.http import HttpRequest

from .bots import BOTS


def is_crawler(request: HttpRequest):
    user_agent = (request.headers.get('User-Agent') or request.headers.get('user-agent') or request.headers.get(
        'user-agent') or '').lower()

    if not user_agent:
        return False

    for bot in BOTS:
        if bot in user_agent:
            return True

    return False
