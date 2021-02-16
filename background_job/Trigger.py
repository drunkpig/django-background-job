from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from tzlocal import get_localzone
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger


class CronJobTrigger(CronTrigger):
    def get_next_fire_time(self):
        now = datetime.now().astimezone(self.timezone)
        dt = super().get_next_fire_time(previous_fire_time=None, now=now)
        delta = dt - now
        return delta.total_seconds(), dt


class IntervalJobTrigger(IntervalTrigger):
    def get_next_fire_time(self):
        now = datetime.now().astimezone(self.timezone)
        dt = super().get_next_fire_time(previous_fire_time=None, now=now)
        delta = dt - now
        return delta.total_seconds(), dt


class OnceJobTrigger(DateTrigger):
    def get_next_fire_time(self):
        now = datetime.now().astimezone(get_localzone())
        dt = super().get_next_fire_time(previous_fire_time=None, now=now)
        delta = dt - now
        return delta.total_seconds(), dt