import time
from django.utils import timezone as tz
from huey import crontab
import huey
from huey.contrib.djhuey import db_periodic_task, db_task
from . import models
from django.conf import settings
from django.core.cache import cache


@db_periodic_task(crontab(minute='*'))
def count_beans():
    now = tz.now()
    schedulers = models.Scheduler.objects.all()
    if not schedulers:
        print('There are no schedulers')
        return
    for scheduler in schedulers:
        if scheduler.must_run(now):
            print('run scheduler', scheduler.name)
            scheduler.last_run = now
            scheduler.save()
        else:
            print('skip scheduler', scheduler.name)


def collect_resource_key(id):
    return 'scheduled:collect_source_' + str(id)


def set_collect_progress(id, value):
    key = collect_resource_key(id)
    cache.set(key, value)


def get_collect_progress(id):
    key = collect_resource_key(id)
    return cache.get(key)


def delete_collect_progress(id):
    key = collect_resource_key(id)
    cache.delete(key)


@db_task()
@settings.HUEY.lock_task('scheduled:collect_source')
def collect_source(id):
    i = 30
    print('start collect source', id)
    set_collect_progress(id, 0)
    while i > 0:
        time.sleep(1)
        i -= 1
        set_collect_progress(id, i)
    print('stop collect source', id)
    delete_collect_progress(id)


def get_collect_resiurce_status(id):
    return cache.get(id)
