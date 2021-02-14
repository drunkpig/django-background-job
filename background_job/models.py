import datetime

from apscheduler.triggers.cron import CronTrigger
from django.db import models

# Create your models here.
from django.utils.safestring import mark_safe


class DjangoJob(models.Model):
    """
    定时任务执行情况
    """
    id = models.CharField(max_length=64, primary_key=True)
    job_name = models.CharField(max_length=128)  # 任务名字
    description = models.TextField(blank=True, null=True)  # job作用描述
    job_function = models.CharField(max_length=128)  # 任务的函数名称
    job_parameters = models.TextField(blank=True)
    trigger_type = models.CharField(max_length=128, choices=[["cron","cron"],["interval",'interval'],
                                                         ['once','once'],['delayedjob', 'delayedjob']]) # cron, delayedjob, interval, once
    trigger_expression = models.CharField(max_length=128) # cron表达式
    max_instances = models.IntegerField(default=1)
    allow_parallel = models.BooleanField(default=False)
    misfire_grace_time = models.IntegerField(default=0)
    log_succ_interval = models.IntegerField(default=0) # 由于成功是大概率，为了减少写库压力可设置间隔多久记录一次成功日志,0则一直写
    log_err_interval = models.IntegerField(default=0)  # 如果遇到连续失败，记录策略

    gmt_update = models.DateTimeField(auto_now=True)  # 最后更新时间
    gmt_created = models.DateTimeField(auto_now_add=True)  # 创建时间

    class Meta:
        ordering = ('gmt_update', )

    def next_run_time(self):
        # TODO 根据 trigger_type
        trigger:CronTrigger = CronTrigger.from_crontab(self.trigger_expression)
        return trigger.get_next_fire_time()


class JobExecHistory(models.Model):
    """
    定时任务执行情况
    """
    RUNNING = "Running"
    #MAX_INSTANCES = u"Max instances reached!"
    #MISSED = u"Missed!"
    ERROR = u"Error!"
    SUCCESS = u"Success"

    id = models.AutoField(primary_key=True)
    job_instance_id = models.CharField(max_length=64, unique=True)  # job实例id
    job = models.ForeignKey(DjangoJob, on_delete=models.CASCADE)
    job_name = models.CharField(max_length=128, verbose_name="任务名称")  # 任务名字
    status = models.CharField(max_length=50, choices=[
        [RUNNING,RUNNING],[SUCCESS,SUCCESS],[ERROR,ERROR]
    ])

    start_tm = models.DateTimeField(auto_now_add=True)  # job开始时间
    end_tm = models.DateTimeField(auto_now=True)  # 结束（成功|失败)时间
    trace_message = models.TextField(blank=True, verbose_name="追踪日志") # 错误记录等
    gmt_update = models.DateTimeField(auto_now=True)  # 最后更新时间
    gmt_created = models.DateTimeField(auto_now_add=True)  # 创建时间

    def html_status(self):
        m = {
            self.RUNNING: "blue",
            # self.MAX_INSTANCES: "yellow",
            # self.MISSED: "yellow",
            self.ERROR: "red",
            self.SUCCESS: "green"
        }

        return mark_safe("<p style=\"color: {}\">{}</p>".format(
            m[self.status],
            self.status
        ))

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