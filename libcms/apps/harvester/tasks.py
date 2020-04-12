from django.utils import timezone

from scheduled.utils import must_run
from . import harvesting
from . import indexing
from . import models


# @db_task(name='harvester:index')
# @settings.HUEY.lock_task('harvester:index')
# @task_status('harvester:index')
def index():
    indexing.index()


# @db_task(name='harvester:index_source')
# @settings.HUEY.lock_task('harvester:index')
# @task_status('harvester:index_source')
def index_source(id):
    indexing.index_source(id)


# @db_task(name='harvester:collect')
# @settings.HUEY.lock_task('harvester:collect')
# @task_status('harvester:collect')
def collect():
    harvesting.collect()


# @db_task(name='harvester:collect_source')
# @settings.HUEY.lock_task('harvester:collect')
# @task_status('harvester:collect_source')
def collect_source(id):
    harvesting.collect_source(id)


# @db_periodic_task(crontab(minute='*'))
def scheduled_collect():
    now = timezone.now()
    print('run scheduled collect')
    for rule in models.HarvestingRule.objects.filter(active=True, scheduled=True):
        if must_run(rule.cron_rule, rule.last_harvested, now):
            print('collect_source', rule.source_id)
            collect_source(rule.source_id)


# @db_periodic_task(crontab(minute='*'))
def scheduled_collect():
    now = timezone.now()
    print('run scheduled collect')
    for rule in models.HarvestingRule.objects.filter(active=True, scheduled=True):
        if must_run(rule.cron_rule, rule.last_harvested, now):
            print('collect_source', rule.source_id)
            collect_source(rule.source_id)


# @db_periodic_task(crontab(minute='*'))
def scheduled_indexing():
    now = timezone.now()
    print('run scheduled indexing')
    for rule in models.IndexingRule.objects.filter(active=True, scheduled=True):
        if must_run(rule.cron_rule, rule.last_indexed, now):
            print('index_source', rule.source_id)
            index_source(rule.source_id)
            rule.last_indexed = now
            rule.save()