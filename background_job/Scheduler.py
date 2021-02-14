import threading
from queue import Queue

from apscheduler.triggers.cron import CronTrigger

from models import DjangoJob


class Scheduler(threading.Thread):
    def __init__(self, queue:Queue, ):
        self.queue = queue
        # load from db
        self.job_list = self.__load_and_sort_by_next_runtm()

    @staticmethod
    def __load_and_sort_by_next_runtm(self):
        jobs = DjangoJob.objects.all()
        job_list = []
        if jobs:
            job_list = sorted(job_list, key=lambda x: x.next_run_time(), reverse=False)

        return job_list

    def run(self):
        pass
        # TODO LOOP：
            # 最后调度时间距离目前的时间 T秒
            # sleep(T)
            # 调用job，放入到queue里
            # 重新排序



