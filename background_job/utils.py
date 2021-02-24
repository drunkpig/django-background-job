import logging

from django.db.models import Max

from background_job.models import DjangoJob, JobExecHistory

logger = logging.getLogger()


def get_max_job_version():
    max_version = DjangoJob.objects.aggregate(Max('version'))  # {'version__max': 5}
    if max_version:
        max_version = max_version['version__max']
    else:
        max_version = 0
    return max_version


def log_job_history(job:DjangoJob, status, result=None, trace_message=None):
    try:
        JobExecHistory.objects.create(job=job, job_name=job.job_name, trigger_type=job.trigger_type,
                                      version=job.version, status=status, result=result, trace_message=trace_message,
                                      )
    except Exception as e:
        logger.exception(e)


def log_job_history_by_id(job_id, status, result=None, trace_message=None):
    try:
        job = DjangoJob.objects.get(id=job_id)
        JobExecHistory.objects.create(job=job, job_name=job.job_name, trigger_type=job.trigger_type,
                                      version=job.version, status=status, result=result, trace_message=trace_message,
                                      )
    except Exception as e:
        logger.exception(e)
