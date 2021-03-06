import copy
import datetime
import json
import uuid

from django.db import models

# Create your models here.
from django.utils.safestring import mark_safe

from background_job.Trigger import CronJobTrigger, IntervalJobTrigger, OnceJobTrigger


class DjangoJob(models.Model):
    """
    定时任务执行情况
    """
    id = models.CharField(max_length=64, primary_key=True)
    job_name = models.CharField(max_length=128)  # 任务名字
    version = models.IntegerField(blank=False, null=False)  # 版本，用于每次重启时选择最大版本运行
    enable = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)  # job作用描述
    job_function = models.CharField(max_length=128, )  # 任务的函数名称
    job_parameters = models.TextField(blank=True, )
    trigger_type = models.CharField(max_length=128, choices=[["cron","cron"],["interval",'interval'],
                                                         ['once','once'],['boot_once','boot_once']]) # cron, delayedjob, interval, once
    trigger_expression = models.CharField(max_length=128) # cron表达式
    max_instances = models.IntegerField(default=1)
    misfire_grace_time = models.IntegerField(default=0)
    coalesce = models.BooleanField(default=False) # 是否把错过的全都执行一遍
    log_succ_interval = models.IntegerField(default=0) # 由于成功是大概率，为了减少写库压力可设置间隔多久记录一次成功日志,0则一直写
    log_err_interval = models.IntegerField(default=0)  # 如果遇到连续失败，记录策略

    gmt_update = models.DateTimeField(auto_now=True)  # 最后更新时间
    gmt_created = models.DateTimeField(auto_now_add=True)  # 创建时间

    class Meta:
        ordering = ('gmt_update', )

    def instance(self):
        instance = copy.copy(self)
        instance.instance_id = str(uuid.uuid4())
        return instance

    def next_run_time(self):
        if self.trigger_type=='cron':
            trigger:CronJobTrigger = CronJobTrigger.from_crontab(self.trigger_expression)
            seconds, dt = trigger.get_next_fire_time()
            return seconds, dt
        elif self.trigger_type=='interval':
            trigger_args = json.loads(self.trigger_expression)
            trigger:IntervalJobTrigger = IntervalJobTrigger(**trigger_args)
            seconds, dt = trigger.get_next_fire_time()
            return seconds, dt
        elif self.trigger_type=='once':
            trigger: OnceJobTrigger = OnceJobTrigger(self.trigger_expression)
            seconds, dt = trigger.get_next_fire_time()
            return seconds, dt
        elif self.trigger_type=='boot_once':
            delay_seconds = 10
            delta = datetime.timedelta(seconds=delay_seconds)
            dt = datetime.datetime.now()+delta
            return delay_seconds, dt
        else:
            raise Exception("*********没有实现的trigger type")# TODO 根据 trigger_type


class DelayedJob(models.Model):
    id = models.AutoField(primary_key=True)
    job_name = models.CharField(max_length=128)  # 任务名字
    version = models.IntegerField(blank=False, null=False)  # 版本，用于每次重启时选择最大版本运行
    enable = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)  # job作用描述
    job_function = models.CharField(max_length=128, )  # 任务的函数名称
    job_parameters = models.TextField(blank=True, )
    retry = models.IntegerField(default=0)
    retry_cnt = models.IntegerField(default=0)

    gmt_update = models.DateTimeField(auto_now=True)  # 最后更新时间
    gmt_created = models.DateTimeField(auto_now_add=True)  # 创建时间

    class Meta:
        ordering = ('gmt_update', )


class JobExecHistory(models.Model):
    """
    任务执行情况
    """
    NEW = "New"
    RUNNING = "Running"
    MAX_INSTANCES = "Max instances reached!"
    MISSED = "Missed!"
    ERROR = "Error!"
    SUCCESS = "Success"
    #id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=64, primary_key=True)
    job = models.ForeignKey(DjangoJob, on_delete=models.CASCADE)
    job_name = models.CharField(max_length=128, verbose_name="任务名称")  # 任务名字
    trigger_type = models.CharField(max_length=128, null=False, verbose_name="任务类型")
    version = models.IntegerField(blank=False, null=False)  # 版本，用于每次重启时选择最大版本运行
    status = models.CharField(max_length=50, choices=[
        [NEW,NEW],[RUNNING,RUNNING],[SUCCESS,SUCCESS],[ERROR,ERROR],
        [MAX_INSTANCES,MAX_INSTANCES],[MISSED,MISSED]
    ])
    result = models.TextField(blank=True, null=True, verbose_name="执行返回结果")
    start_tm = models.DateTimeField(auto_now_add=True)  # job开始时间
    end_tm = models.DateTimeField(auto_now=True)  # 结束（成功|失败)时间
    trace_message = models.TextField(blank=True, null=True, verbose_name="追踪日志") # 错误记录等
    gmt_update = models.DateTimeField(auto_now=True)  # 最后更新时间
    gmt_created = models.DateTimeField(auto_now_add=True)  # 创建时间

    def html_status(self):
        m = {
            self.NEW: "gray",
            self.RUNNING: "blue",
            self.MAX_INSTANCES: "yellow",
            self.MISSED: "yellow",
            self.ERROR: "red",
            self.SUCCESS: "green"
        }

        return mark_safe("<p style=\"color: {}\">{}</p>".format(
            m[self.status],
            self.status
        ))
    html_status.verbose_name="任务状态"

    def duration(self):
        """
        任务持续时长
        :return:
        """
        delta = self.end_tm-self.start_tm
        if delta < datetime.timedelta(milliseconds=0):
            delta = "00:00:00"
        return str(delta)

    class Meta:
        ordering = ('-start_tm', )


class ActionLog(models.Model):
    id = models.AutoField(primary_key=True)
    action = models.CharField(max_length=256, verbose_name="操作")  #
    op_host = models.CharField(max_length=128, verbose_name="操作来源")  # 哪台设备的操作
    gmt_update = models.DateTimeField(auto_now=True)  # 最后更新时间
    gmt_created = models.DateTimeField(auto_now_add=True)  # 创建时间
