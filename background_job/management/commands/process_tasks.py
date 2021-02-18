# -*- coding: utf-8 -*-
import logging
import queue
import random
import sys
import time
from importlib import import_module
from logging.config import fileConfig

from django import VERSION
from django.core.management.base import BaseCommand
from django.utils import autoreload

from background_job.JobProcessor import JobProcessor
from background_job.Scheduler import Scheduler
fileConfig("logging.ini")
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run tasks that are scheduled to run on the queue'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        # self.sig_manager = None
        # self._tasks = tasks

    def run(self, *args, **options):
        autodiscover()
        start_job_processor()

    def handle(self, *args, **options):
        self.run(*args, **options)


def autodiscover():
    '''autodiscover tasks.py files in much the same way as admin app'''
    import imp
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue
        try:
            imp.find_module('jobs', app_path)
        except ImportError:
            continue

        import_module("%s.jobs" % app)
        logger.info("load module %s.jobs", app)


def start_job_processor():
    job_queue = queue.Queue()
    sched = Scheduler(queue=job_queue)
    sched.start()
    processor = JobProcessor(job_queue)
    processor.start()
