import datetime

from django.contrib import admin
from django.db.models import Avg
from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import now
from .models import DjangoJob, JobExecHistory, DelayedJob


@admin.register(DjangoJob)
class DjangoJobAdmin(admin.ModelAdmin):
    list_display = ["job_name_html",  "job_function",  "job_parameters",
                    "trigger_type", "trigger_expression", "max_instances",
                    "misfire_grace_time", "coalesce",
                    "log_succ_interval","log_err_interval",
                    "gmt_update", "gmt_created"]
    actions = []

    def job_name_html(self, obj):
        link = reverse("admin:background_job_djangojob_change", args=[obj.id])
        return format_html('<a href="{}">{}</a>', link, obj.job_name)

    job_name_html.short_description="Job Name"


@admin.register(DelayedJob)
class DelayedJobAdmin(admin.ModelAdmin):
    list_display = ["job_name_html",  "job_function",  "job_parameters",
                    "retry", "retry_cnt",
                    "gmt_update", "gmt_created"]
    actions = []

    def job_name_html(self, obj):
        link = reverse("admin:background_job_delayedjob_change", args=[obj.id])
        return format_html('<a href="{}">{}</a>', link, obj.job_name)

    job_name_html.short_description="Job Name"


@admin.register(JobExecHistory)
class DjangoJobExecAdmin(admin.ModelAdmin):
    list_display = ["id", "job_name",  "trace_message", "html_status", "duration", "start_tm", "end_tm"]
    list_filter = ["job_name",  "status"]