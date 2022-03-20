from django.db import models
from django.db.models import QuerySet


class ApplicationQueryset(QuerySet["Application"]):
    def bulk_create_applications(self):
        from job.models import Job

        keys = Job.objects.values_list("key", flat=True)
        applications = [Application(job_key=key) for key in keys]
        self.bulk_create(applications, ignore_conflicts=True)


class Application(models.Model):
    """
    Represents a job application, or info
    related to applying to a job.
    """

    objects = ApplicationQueryset.as_manager()

    APPLY_VALUES = ["yes", "no", "maybe"]
    APPLY_CHOICES: list[tuple[str, str]] = [
        (v, v.lower().title()) for v in APPLY_VALUES
    ]

    job_key: models.CharField = models.CharField(
        max_length=60,
        primary_key=True,
    )
    is_applying: models.CharField = models.CharField(
        max_length=5,
        choices=APPLY_CHOICES,
        null=True,
    )
    notes: models.TextField = models.TextField(null=True)
