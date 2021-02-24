import functools, inspect
import logging, hashlib, json
from datetime import datetime
from background_job.models import DjangoJob, DelayedJob
from background_job.utils import get_max_job_version, log_action

logger = logging.getLogger(__name__)


JOB_VERSION = get_max_job_version() + 1


def md5(astring):
    x = hashlib.md5(astring.encode()).hexdigest()
    return x


def __x_job(name,  trigger_type, trigger_exp, enable=True,  max_instances=1, misfire_grace_time=3, coalesce=False,
             log_succ_interval=0, log_err_interval=0, description=None, args=None, kwargs=None):
    """

    """
    def inner(func):
        job_id = md5(name)
        mod_func = f"{inspect.getmodule(func).__name__}.{func.__name__ }"
        job_parameters = {
                        'args': tuple(args) if args is not None else (),
                        'kwargs': dict(kwargs) if kwargs is not None else {},
        }
        values = { "job_name":name, "description":description,
                   "job_function":mod_func, "trigger_type":trigger_type,
                   "job_parameters":json.dumps(job_parameters), "version":JOB_VERSION,
                   "trigger_expression":trigger_exp, "max_instances":max_instances,
                    "misfire_grace_time":misfire_grace_time, "coalesce":coalesce,
                   "log_succ_interval":log_succ_interval, "log_err_interval":log_err_interval,}
        obj, created  = DjangoJob.objects.update_or_create(id=job_id,
                                           defaults=values)
        if created:
            # 如果是新建，那么就把代码中的enable状态写入进去，否则保持手工修改的结果
            obj.enable = enable
            obj.save()
            log_action(f"create new job: {name}")
        else:
            log_action(f"update new job: {name}")

        @functools.wraps(func)
        def real_func(*args, **kwargs):
            return func(*args, **kwargs)
        return real_func
    return inner


def cron_job(name, cron, enable=True,  max_instances=1, misfire_grace_time=2, coalesce=False,
             log_succ_interval=0, log_err_interval=0, description=None, args=None, kwargs=None):
    """
    name: 任务名称，自己随便写
    cron: 字符串， cron表达式  TODO 验证表达式
    parallel: 是否允许任务并行，当最大实例为1的时候
    max_instances: 同一次触发最大的运行个数
    misfire_grace_time: 超出执行点多久可以弥补
    """
    return __x_job(name, 'cron', cron,  max_instances=max_instances, enable=enable,
                   misfire_grace_time=misfire_grace_time, coalesce=coalesce,
                   log_succ_interval=log_succ_interval, log_err_interval=log_err_interval,
                   description=description, args=args, kwargs=kwargs)


def interval_job(name, weeks=0, days=0, hours=0, minutes=0, seconds=0, start_date=None, end_date=None,
                 max_instances=1, misfire_grace_time=2, coalesce=False, enable=True,
                 log_succ_interval=0, log_err_interval=0, description=None, args=None, kwargs=None):
    interval_exp = json.dumps({"weeks":weeks,"days":days,"hours":hours,"minutes":minutes,"seconds":seconds,
                               "start_date":start_date,"end_date":end_date,})
    return __x_job(name, 'interval', interval_exp, max_instances=max_instances,
                   misfire_grace_time=misfire_grace_time, coalesce=coalesce, enable=enable,
                   log_succ_interval=log_succ_interval, log_err_interval=log_err_interval,
                   description=description, args=args, kwargs=kwargs)


def once_job(name, run_at,  max_instances=1, misfire_grace_time=2, coalesce=False, enable=True,
             log_succ_interval=0, log_err_interval=0, description=None, args=None, kwargs=None):
    return __x_job(name, 'once', run_at, max_instances=max_instances,
                   misfire_grace_time=misfire_grace_time, coalesce=coalesce, enable=enable,
                   log_succ_interval=log_succ_interval, log_err_interval=log_err_interval,
                   description=description, args=args, kwargs=kwargs)


def boot_job(name, enable=True, description=None, args=None, kwargs=None):
    API_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    run_at = datetime.now().strftime(API_DATE_FORMAT)
    return __x_job(name, 'boot_once', run_at, enable=enable, description=description, args=args, kwargs=kwargs)


def delayed_job(name, retry=3, enable=True, description=None):
    """
    id: 保证对同一个func唯一性
    nonce: 全局唯一，可用来保证幂等性
    retry: 重试多少次，如果为-1则要保证一定能完成

    """
    def inner(func):
        @functools.wraps(func)
        def real_func(*args, **kwargs):
            mod_func = f"{inspect.getmodule(func).__name__}.{func.__name__}"
            job_parameters = {
                'args': tuple(args) if args is not None else (),
                'kwargs': dict(kwargs) if kwargs is not None else {},
            }
            values = {"job_name": name, "description": description,
                      "job_function": mod_func, "job_parameters": json.dumps(job_parameters),
                      "retry":retry, "enable":enable, "version":JOB_VERSION,
                       }
            DelayedJob.objects.create(**values)

        return real_func

    return inner
