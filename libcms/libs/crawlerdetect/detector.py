from django.http import HttpRequest

from .bots import BOTS


def is_crawler(request: HttpRequest):
    user_agent = (request.META.get('HTTP_USER_AGENT')or '').lower()
    if not user_agent:
        return False

    for bot in BOTS:
        if bot in user_agent:
            return True

    return False
