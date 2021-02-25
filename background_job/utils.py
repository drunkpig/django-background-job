import logging, socket

from django.db.models import Max

from background_job.models import DjangoJob, JobExecHistory, ActionLog

logger = logging.getLogger()


def get_max_job_version():
    max_version = DjangoJob.objects.aggregate(Max('version'))  # {'version__max': 5}
    if max_version:
        max_version = max_version['version__max']
    if max_version is None:
        max_version = 0

    return max_version


def log_job_history(job, status, result=None, trace_message=None):
    logger.info(f"job name={job.job_name}, status ={status}, instance_id={job.instance_id}")
    try:
        id = job.instance_id
        values = {"job_name":job.job_name, "job":job, "trigger_type":job.trigger_type,
                  "version":job.version, "status":status, "result":result, "trace_message":trace_message}
        JobExecHistory.objects.update_or_create(id=id, defaults=values)
    except Exception as e:
        logger.exception(e)
        logger.error(f"job name={job.job_name}, status ={status}, instance_id={job.instance_id}")


def log_job_history_by_id(job_id, job_instance_id, status, result=None, trace_message=None):
    logger.info(f"job name={job_id}, status ={status}, instance_id={job_instance_id}")
    try:
        id = job_instance_id
        job = DjangoJob.objects.get(id=job_id)
        values = {"job_name": job.job_name, "job": job, "trigger_type": job.trigger_type,
                  "version": job.version, "status": status, "result": result, "trace_message": trace_message}

        JobExecHistory.objects.update_or_create(id=id, defaults=values)
    except Exception as e:
        logger.exception(e)


def log_action(action):
    try:
        host_name = socket.gethostname()
        ActionLog.objects.create(action=action, op_host=host_name)
    except Exception as e:
        logger.exception(e)
