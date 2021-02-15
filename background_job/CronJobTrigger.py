from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta


class CronJobTrigger(CronTrigger):
    def get_next_fire_time(self):
        now = datetime.now().astimezone(self.timezone)
        dt = super().get_next_fire_time(previous_fire_time=None, now=now)
        delta = dt - now
        return delta.total_seconds(), dt
