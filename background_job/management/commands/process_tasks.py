# -*- coding: utf-8 -*-
import logging
import random
import sys
import time
from importlib import import_module

from django import VERSION
from django.core.management.base import BaseCommand
from django.utils import autoreload


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run tasks that are scheduled to run on the queue'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        # self.sig_manager = None
        # self._tasks = tasks

    def run(self, *args, **options):
        autodiscover()

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