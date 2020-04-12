from crontab import CronTab as Ct
import datetime as dt


def must_run(cron_rule, last_run, run_time):
    if last_run is None:
        return True

    c = Ct(cron_rule)
    return run_time + dt.timedelta(seconds=c.previous(run_time)) >= last_run
