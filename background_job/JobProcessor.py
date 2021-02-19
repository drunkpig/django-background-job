import threading
import time
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, Future
import importlib, json, logging
import multiprocessing


class JobProcessor(threading.Thread):
    LOGGER = logging.getLogger()

    def __init__(self, queue:Queue,):
        super().__init__()
        self.setDaemon(False)
        self.queue = queue
        self.threadpool = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()*2)

    def run(self):
        while True:
            try:
                job = self.queue.get(block=True)
                parameters = json.loads(job.job_parameters)
                self.__call(job.id, job.job_function, *parameters['args'], **parameters['kwargs'])
            except Exception as e:
                self.LOGGER.exception(e)
                # TODO log db error

    def __call(self, job_id, function_string, *args, **kwargs):
        """

        """
        try:
            mod_name, func_name = function_string.rsplit('.', 1)
            mod = importlib.import_module(mod_name)
            func = getattr(mod, func_name)
            future = self.threadpool.submit(func, *args, **kwargs)
            future.job_id=job_id
            future.add_done_callback(self.__call_succ)
        except Exception as e:
            self.LOGGER.exception(e)
            # TODO log it

    def __call_succ(self, future: Future):  # TODO exception
        """

        """
        if future.cancelled():
            self.LOGGER.warning(">>>> cancelled")
            # TODO log db
        elif future.done():
            error = future.exception()
            if error:
                self.LOGGER.error(">>>>%s", error)
                # TODO log db
            else:
                result = future.result()
                self.LOGGER.info(">>>>%s", result)
                # TODO log db，含函数结果
        self.LOGGER.info("%s, %s", future.job_id, future.result())
