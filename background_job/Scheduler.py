import json
import logging
import threading
import time
from queue import Queue
import importlib
import sched

from background_job.models import DjangoJob

logger = logging.getLogger()


class Scheduler(threading.Thread):
    def __init__(self, queue:Queue, ):
        super().__init__()
        self.setDaemon(False)
        self.queue = queue
        # load from db
        self.job_list = self.__load_jobs()
        self.timer = sched.scheduler(time.time, time.sleep)

    @staticmethod
    def __load_jobs():
        jobs = DjangoJob.objects.all()
        return jobs

    def run(self):
        if len(self.job_list)<=0:
            logger.info("no task to schedule")
        else:
            for job in self.job_list:
                self.__lunch_job(job)
        while True:
            self.timer.run(blocking=True)
            logger.warning("调度无任务，暂时退出")
            time.sleep(1)

    def __lunch_job(self, job):
        seconds_to_wait, _ = job.next_run_time()
        if seconds_to_wait<0 and abs(seconds_to_wait)<=job.misfire_grace_time:
            seconds_to_wait = 0
        elif seconds_to_wait<0:
            # TODO 根据记录决定是否记录
            logger.info("task [%s] missed! (delay, misfire_grace_time)=(%s, %s)", job.job_function, seconds_to_wait, job.misfire_grace_time)
            return
        logger.info("task [%s] will invoke after [%f] seconds later", job.job_function, seconds_to_wait)
        self.timer.enter(seconds_to_wait, 0, self.__fire_job, argument=(job, ))

    def __fire_job(self, job):
        # self.queue.put(job, block=True)

        seconds_to_wait,_ = job.next_run_time()
        if seconds_to_wait is not None and seconds_to_wait>0:
            self.timer.enter(seconds_to_wait, 0, self.__fire_job, argument=(job,))
            logger.info("task [%s] will invoke after [%f] seconds later", job.job_function, seconds_to_wait)

        parameters = json.loads(job.job_parameters) # TODO 避免直接call, 这里为了测试
        self.__call(job.job_function, *parameters['args'], **parameters['kwargs'])

    def __call(self, function_string, *args, **kwargs):
        mod_name, func_name = function_string.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        result = func(*args, **kwargs)
