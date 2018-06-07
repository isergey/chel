from django.shortcuts import HttpResponse
from django.views.decorators.http import condition
from . import models

def _latest_update(request):
    contents = models.RobotsTxt.objects.all()[:1]
    if contents:
        return contents[0].update_date
    return None


@condition(last_modified_func=_latest_update)
def index(request):
    contents = models.RobotsTxt.objects.all()[:1]
    content = ''
    if contents:
        content = contents[0].content
    return HttpResponse(content=content, content_type='text/plain')