import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import importlib,json


class JobProcessor(threading.Thread):
    def __init__(self, queue:Queue,):
        super().__init__()
        self.setDaemon(False)
        self.queue = queue
        self.threadpool = ThreadPoolExecutor(128)

    def run(self):
        for job in self.queue:
            parameters = json.loads(job.job_parameters)
            self.__call(job.job_function, *parameters['args'], **parameters['kwargs'])

    def __call(self, function_string, *args, **kwargs):
        mod_name, func_name = function_string.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        result = func(*args, **kwargs)