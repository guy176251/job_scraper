from django.apps import AppConfig


class JobConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "job"

    def ready(self):
        """
        Put things in here that should be run once app is ready.
        """
        # import job.signals
