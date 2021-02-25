import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, Future
import importlib, json, logging
import multiprocessing

from background_job.models import JobExecHistory
from background_job.utils import log_job_history_by_id, log_job_history


class JobProcessor(threading.Thread):
    LOGGER = logging.getLogger()

    def __init__(self, queue: Queue, ):
        super().__init__()
        self.setDaemon(False)
        self.queue = queue
        self.threadpool = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 2)

    def run(self):
        while True:
            job = None
            try:
                job = self.queue.get(block=True)
                parameters = json.loads(job.job_parameters)
                log_job_history(job, status=JobExecHistory.RUNNING, result=None, trace_message=None)
                self.__call(job.id, job.instance_id, job.job_function, *parameters['args'], **parameters['kwargs'])

            except Exception as e:
                self.LOGGER.exception(e)
                log_job_history(job, status=JobExecHistory.ERROR, result=None, trace_message=e)

    def __call(self, job_id, job_instance_id, function_string, *args, **kwargs):
        """

        """
        mod_name, func_name = function_string.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        future = self.threadpool.submit(func, *args, **kwargs)
        future.job_id = job_id
        future.instance_id = job_instance_id
        future.function_string = function_string
        future.add_done_callback(self.__call_succ)

    def __call_succ(self, future: Future):  # TODO exception
        """

        """
        job_id = future.job_id
        job_instance_id = future.instance_id
        function_string = future.function_string
        try:
            if future.cancelled():
                self.LOGGER.warning("%s cancelled", function_string)
                log_job_history_by_id(job_id, job_instance_id, status=JobExecHistory.MISSED, result=None, trace_message="job cancelled")
            elif future.done():
                error = future.exception()
                if error:
                    self.LOGGER.error("%s ERROR: %s", function_string, error)
                    log_job_history_by_id(job_id, job_instance_id, status=JobExecHistory.ERROR, result=None, trace_message=error)
                else:
                    result = future.result()
                    self.LOGGER.info("%s return: %s", function_string, result)
                    log_job_history_by_id(job_id, job_instance_id, status=JobExecHistory.SUCCESS, result=result, trace_message=None)
        except Exception as e:
            self.LOGGER.exception(e)
