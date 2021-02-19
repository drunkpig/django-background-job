import json
import logging
import queue
import threading
import time
from queue import Queue

import sched

from background_job.models import DjangoJob

logger = logging.getLogger()


class Scheduler(threading.Thread):
    def __init__(self, queue:Queue, ):
        super().__init__()
        self.setDaemon(False)
        self.queue = queue
        # load from db
        self.__load_jobs()
        self.timer = sched.scheduler(time.time, time.sleep)

    def __load_jobs(self):
        jobs = DjangoJob.objects.all()
        self.job_list = jobs

    def run(self):
        if len(self.job_list)<=0:
            logger.info("no task to schedule")
        else:
            for job in self.job_list:
                if job.trigger_type in ['cron', 'interval']:
                    self.__lunch_periodical_job(job)
                elif job.trigger_type=='once':
                    self.__lunch_once_job(job)
                else:
                    self.__lunch_once_boot_job(job)
        while True:
            self.timer.run(blocking=True)
            logger.warning("调度无任务，暂时休眠")
            time.sleep(1)

    def __lunch_periodical_job(self, job):
        seconds_to_wait, _ = job.next_run_time()
        if seconds_to_wait<0 and abs(seconds_to_wait)<=job.misfire_grace_time: # 是否在指定时间容错范围内可以执行
            seconds_to_wait = 0
        elif seconds_to_wait<0:
            # TODO 根据loglevel决定是否记录
            logger.info("task [%s] missed! (delay, misfire_grace_time)=(%s, %s)", job.job_function, seconds_to_wait, job.misfire_grace_time)
            return
        logger.info("task [%s] will invoke after [%f] seconds later", job.job_function, seconds_to_wait)
        self.timer.enter(seconds_to_wait, 0, self.__fire_job, argument=(job, ))

    def __lunch_once_job(self, job):
        seconds_to_wait, _ = job.next_run_time()
        if seconds_to_wait < 0 and abs(seconds_to_wait) <= job.misfire_grace_time:  # 是否在指定时间容错范围内可以执行
            seconds_to_wait = 0
        elif seconds_to_wait < 0:
            # TODO 根据loglevel决定是否记录
            logger.info("task [%s] missed! (delay, misfire_grace_time)=(%s, %s)", job.job_function, seconds_to_wait,
                        job.misfire_grace_time)
            return
        logger.info("task [%s] will invoke after [%f] seconds later", job.job_function, seconds_to_wait)
        self.timer.enter(seconds_to_wait, 0, self.__fire_once_job, argument=(job,))

    def __fire_once_job(self, job):
        self.__lunch_once_boot_job(job)

    def __lunch_once_boot_job(self, job):
        try:
            self.queue.put_nowait(job)
        except queue.Full as e:
            logger.exception(e)
            # TODO log job missed!
        except Exception as e:
            logger.exception(e)
            # TODO log job missed!

    def __fire_job(self, job:DjangoJob):
        try:
            self.queue.put_nowait(job)
        except queue.Full as e:
            logger.exception(e)
            # TODO log job missed!
        except Exception as e:
            logger.exception(e)
            # TODO log job missed!

        seconds_to_wait,_ = job.next_run_time()
        if seconds_to_wait>0 or abs(seconds_to_wait) <= job.misfire_grace_time:
            self.timer.enter(seconds_to_wait, 0, self.__fire_job, argument=(job,))
            logger.info("task [%s] will invoke after [%f] seconds later", job.job_function, seconds_to_wait)
        else:
            logger.info("task [%s] missed! (delay, misfire_grace_time)=(%s, %s)", job.job_function, seconds_to_wait,
                        job.misfire_grace_time)
            # TODO log job missed!
