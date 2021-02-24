import json
import logging
import queue
import threading
import time
from queue import Queue

import sched, datetime

from django.db.models import Max

from background_job.models import DjangoJob, JobExecHistory
from background_job.utils import get_max_job_version, log_job_history

logger = logging.getLogger()


class Scheduler(threading.Thread):
    def __init__(self, queue:Queue, ):
        super().__init__()
        self.setDaemon(False)
        self.queue = queue
        # load from db
        self.__load_jobs()
        self.max_update_tm = self.__get_max_update_tm()
        self.timer = sched.scheduler(time.time, time.sleep)

    def __load_jobs(self):
        jobs = self.__get_all_jobs()
        job_list = {}
        if jobs:
            for j in jobs:
                job_list[j.id] = j
        self.job_list = job_list

    def __get_all_jobs(self):
        self.max_version = get_max_job_version()
        jobs = DjangoJob.objects.filter(enable=True, version=self.max_version).all()
        return jobs

    def __get_max_update_tm(self):
        x = DjangoJob.objects.aggregate(Max('gmt_update'))
        if x:
            return x['gmt_update__max']
        else:
            return datetime.datetime.now()

    def run(self):
        if len(self.job_list.keys())<=0:
            logger.info("no task to schedule")
        else:
            for job in self.job_list.values():
                if job.enable:
                    if job.trigger_type in ['cron', 'interval']:
                        self.__lunch_periodical_job(job)
                    elif job.trigger_type=='once':
                        self.__lunch_once_job(job)
                    else:
                        self.__lunch_once_boot_job(job)
        self.timer.enter(60, 1, self.__reload_job) # 更新job
        while True:
            self.timer.run(blocking=True)
            logger.warning("调度无任务，暂时休眠")
            time.sleep(1)

    def __reload_job(self):
        """
        新增、删除、更改了

        """
        self.timer.enter(60, 1, self.__reload_job)  # 更新job
        jobs = DjangoJob.objects.filter(version=self.max_version, gmt_update__gt=self.max_update_tm).all()
        if jobs:
            for j in jobs:
                id = j.id
                enable = j.enable
                # 1, 删除，enable->disable, disable->enable
                if enable and id not in self.job_list.keys():
                    # 从disable -> enable, 新调度 
                    if j.trigger_type in ['cron', 'interval']:
                        self.job_list[id] = j
                        self.__lunch_periodical_job(j)
                        logger.info("enable job=%s", j.job_name)
                        # TODO log switch log
                elif enable and id in self.job_list.keys():
                    # enable -> disable ---> enable
                    self.job_list[id].enable = True
                    self.__lunch_periodical_job(self.job_list[id])
                elif not enable and id in self.job_list.keys():
                    # 从enable ->disable #停止调度
                    self.job_list[id].enable = False
                    self.job_list[id].job_parameters = j.job_parameters
                    self.job_list[id].job_name = j.job_name
                    self.job_list[id].job_function = j.job_function
                    self.job_list[id].trigger_expression = j.trigger_expression
                    logger.info("disable job=%s", j.job_name)
                    # TODO log switch log
                # 删除无法感知，除非整体重新加载。
        else:
            logger.info("没有发现更新的job")

        self.max_update_tm = self.__get_max_update_tm()

    def __lunch_periodical_job(self, job):
        seconds_to_wait, _ = job.next_run_time()
        if seconds_to_wait<0 and abs(seconds_to_wait)<=job.misfire_grace_time: # 是否在指定时间容错范围内可以执行
            seconds_to_wait = 0
        elif seconds_to_wait<0:
            # TODO 根据loglevel决定是否记录
            logger.info("task [%s] missed! (delay, misfire_grace_time)=(%s, %s)", job.job_function, seconds_to_wait, job.misfire_grace_time)
            log_job_history(job, status=JobExecHistory.MISSED, result=None, trace_message=None)
            return
        logger.info("task [%s] will invoke after [%f] seconds later", job.job_function, seconds_to_wait)
        evt = self.timer.enter(seconds_to_wait, 0, self.__fire_job, argument=(job, ))
        job.evt = evt

    def __lunch_once_job(self, job):
        seconds_to_wait, _ = job.next_run_time()
        if seconds_to_wait < 0 and abs(seconds_to_wait) <= job.misfire_grace_time:  # 是否在指定时间容错范围内可以执行
            seconds_to_wait = 0
        elif seconds_to_wait < 0:
            log_job_history(job, status=JobExecHistory.MISSED, result=None, trace_message=f"delay ~ misfire_grace_time")
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
            log_job_history(job, status=JobExecHistory.NEW, result=None, trace_message=None)
        except queue.Full as e:
            logger.exception(e)
            log_job_history(job, status=JobExecHistory.MISSED, result=None, trace_message=e)
        except Exception as e:
            logger.exception(e)
            log_job_history(job, status=JobExecHistory.MISSED, result=None, trace_message=e)

    def __fire_job(self, job:DjangoJob):
        try:
            self.queue.put_nowait(job)
            log_job_history(job, status=JobExecHistory.NEW, result=None, trace_message=None)
        except queue.Full as e:
            logger.exception(e)
            log_job_history(job, status=JobExecHistory.MISSED, result=None, trace_message=e)
        except Exception as e:
            logger.exception(e)
            log_job_history(job, status=JobExecHistory.MISSED, result=None, trace_message=e)

        seconds_to_wait,_ = job.next_run_time()
        if seconds_to_wait>0 or abs(seconds_to_wait) <= job.misfire_grace_time:
            if job.enable:
                self.timer.enter(seconds_to_wait, 0, self.__fire_job, argument=(job,))
                logger.info("task [%s] will invoke after [%f] seconds later", job.job_function, seconds_to_wait)
        else:
            logger.info("task [%s] missed! (delay, misfire_grace_time)=(%s, %s)", job.job_function, seconds_to_wait,
                        job.misfire_grace_time)
            log_job_history(job, status=JobExecHistory.MISSED, result=None, trace_message=f"delay ~ misfire_grace_time")
