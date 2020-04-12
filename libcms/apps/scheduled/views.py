from django.shortcuts import render, redirect, HttpResponse
from . import tasks
from django.conf import settings
from huey.contrib.djhuey import HUEY
import huey


# Create your views here.
def index(request):
    # for res in settings.HUEY.ge():
    #     print(res)
    # tasks = []
    # for task_id in settings.HUEY.get_tasks():
    #     print(settings.HUEY._get_task_metadata(task_id))
    #     tasks.append(settings.HUEY.get(task_id))
    print(tasks.get_collect_progress('1'))
    return render(request, 'index.html', {
        # 'tasks': tasks
    })


def run_collect_source(request):
    id = request.GET.get('id')
    res = tasks.collect_source(id)
    return redirect('/')


def get_task_status(request):
    id = request.GET.get('id')
    task = HUEY.result(id)
    print(task)
    return HttpResponse('id')
