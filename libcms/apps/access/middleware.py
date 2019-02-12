from django.conf import settings
from django.shortcuts import HttpResponse

DEFAULT_DISALLOW_BOTS = [
    'ahrefsbot',
]

DISALLOW_BOTS = getattr(settings, 'ACCESS_DISALLOW_BOTS', DEFAULT_DISALLOW_BOTS)


class AccessMiddleware:
    def process_response(self, request, response):
        for bot in DISALLOW_BOTS:
            if bot in request.META.get('HTTP_USER_AGENT', '').lower():
                return HttpResponse(status=410)
        return response
