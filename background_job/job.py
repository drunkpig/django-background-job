import functools, inspect
import logging, hashlib, json
from background_job.models import DjangoJob

logger = logging.getLogger(__name__)


def md5(astring):
    x = hashlib.md5(astring.encode()).hexdigest()
    return x


def cron_job(name, cron,  max_instances=1, misfire_grace_time=0, coalesce=False,
             log_succ_interval=0, log_err_interval=0, description=None, args=None, kwargs=None):
    """
    name: 任务名称，自己随便写
    cron: 字符串， cron表达式  TODO 验证表达式
    parallel: 是否允许任务并行，当最大实例为1的时候
    max_instances: 同一次触发最大的运行个数
    misfire_grace_time: 超出执行点多久可以弥补
    """
    def inner(func):
        job_id = md5(name)
        mod_func = f"{inspect.getmodule(func).__name__}.{func.__name__ }"
        job_parameters = {
                        'args': tuple(args) if args is not None else (),
                        'kwargs': dict(kwargs) if kwargs is not None else {},
        }
        values = { "job_name":name, "description":description,
                   "job_function":mod_func, "trigger_type":'cron',
                   "job_parameters":json.dumps(job_parameters),
                   "trigger_expression":cron, "max_instances":max_instances,
                    "misfire_grace_time":misfire_grace_time, "coalesce":coalesce,
                   "log_succ_interval":log_succ_interval, "log_err_interval":log_err_interval,}
        DjangoJob.objects.update_or_create(id=job_id,
                                           defaults=values)
        # print( inspect.getfullargspec(func))
        #
        # print(inspect.getmodule(func))
        # print(inspect.signature(func))

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
