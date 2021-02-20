from django.db.models import Max

from background_job.models import DjangoJob


def get_max_job_version():
    max_version = DjangoJob.objects.aggregate(Max('version'))  # {'version__max': 5}
    if max_version:
        max_version = max_version['version__max']
    else:
        max_version = 0
    return max_version