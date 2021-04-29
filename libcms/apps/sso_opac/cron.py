from django_cron import CronJobBase, Schedule


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 120  # every 2 hours
    RETRY_AFTER_FAILURE_MINS = 5
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'my_app.my_cron_job'  # a unique code

    def do(self):
        pass  # do your thing here
