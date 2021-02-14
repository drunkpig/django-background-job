import functools, inspect
import logging, hashlib
from background_job.models import DjangoJob

logger = logging.getLogger(__name__)


def md5(astring):
    x = hashlib.md5(astring.encode()).hexdigest()
    return x


def cron_job(name, cron,  max_instances=1, allow_parallel=False, misfire_grace_time=0,
             log_succ_interval=0, log_err_interval=0, description=None):
    """
    name: 任务名称，自己随便写
    cron: 字符串， cron表达式  TODO 验证表达式
    parallel: 是否允许任务并行，当最大实例为1的时候
    max_instances: 同一次触发最大的运行个数
    misfire_grace_time: 超出执行点多久可以弥补
    """
    def inner(func):
        job_id = md5(name)
        DjangoJob.objects.update_or_create(id=job_id, job_name=name, description=description,
                                           job_function=func.__name__, trigger_type='cron',
                                           trigger_expression=cron, max_instances=max_instances,
                                           allow_parallel=allow_parallel, misfire_grace_time=misfire_grace_time,
                                           log_succ_interval=log_succ_interval, log_err_interval=log_err_interval)
        print( inspect.getfullargspec(func))
        print(inspect.signature(func))

        @functools.wraps(func)
        def real_func(*args, **kwargs):
            func(*args, **kwargs)

        return real_func
    return inner


def interval_job():
    pass


def once_job():
    pass


def delayed_job():
    pass
