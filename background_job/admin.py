import datetime

from django.contrib import admin
from django.db.models import Avg
from django.utils.timezone import now
from .models import DjangoJob, JobExecHistory


@admin.register(DjangoJob)
class DjangoJobAdmin(admin.ModelAdmin):
    list_display = ["id", "job_name", "description", "job_function",  "job_parameters", "gmt_update", "gmt_created"]
    actions = []


@admin.register(JobExecHistory)
class DjangoJobExecAdmin(admin.ModelAdmin):
    list_display = ["id", "job_name", "job_instance_id", "trace_message", "html_status", "duration", "start_tm", "end_tm"]
    list_filter = ["job_name",  "status"]