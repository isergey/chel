import datetime as dt
from crontab import CronTab as Ct
from django.db import models


class Scheduler(models.Model):
    active = models.BooleanField(default=True)
    cron = models.CharField(
        max_length=64,
        blank=True,
        default='* * * * *'
    )
    last_run = models.DateTimeField(null=True, blank=True)
    name = models.CharField(
        max_length=128
    )

    def must_run(self, run_time):
        if not self.active or not self.cron:
            return False

        if self.last_run is None:
            return True

        c = Ct(self.cron)
        return run_time + dt.timedelta(seconds=c.previous(run_time)) >= self.last_run

    def __str__(self):
        return self.name + ' ' + self.cron
