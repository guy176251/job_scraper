from django.core.management.base import BaseCommand

from job.processors import BackupProcessor, MainProcessor


class Command(BaseCommand):
    def handle(self, *args, **options):
        BackupProcessor.restore()
        MainProcessor.process()
