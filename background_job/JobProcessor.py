import threading
import time
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, Future
import importlib, json, logging
import multiprocessing
from functools import partial


def _picklable_func(func, *args, **kwargs):
    """
    再封装一次的原因如下
    https://stackoverflow.com/questions/49899351/restrictions-on-dynamically-created-functions-with-concurrent-futures-processpoo
    """
    myfunc = partial(func, *args)
    return myfunc


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

    def call_succ(self, future:Future):  # TODO exception
        """

        """
        if future.cancelled():
            self.LOGGER.warning(">>>> cancelled")
        elif future.done():
            error = future.exception()
            if error:
                self.LOGGER.error(">>>>%s", error)
            else:
                result = future.result()
                self.LOGGER.info(">>>>%s", result)
        self.LOGGER.info("%s, %s", future.function_string, future.result())

    def __call(self, job_id, function_string, *args, **kwargs):
        """

        """
        mod_name, func_name = function_string.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        future = self.threadpool.submit(_picklable_func(func, *args, **kwargs),  **kwargs)
        future.function_string=function_string
        future.add_done_callback(self.call_succ)
        return future
