from time import perf_counter
from typing import Type

from .backup import BackupProcessor
from .companies import CompanyAliasProcessor
from .info import Info, InfoProcessor
from .requirements import RequirementProcessor
from .types import JobProcessor


class MainProcessor:
    """
    Runs all of the job information processors.
    """

    processors: list[Type[JobProcessor]] = [
        InfoProcessor,
        RequirementProcessor,
        CompanyAliasProcessor,
        BackupProcessor,
    ]

    @classmethod
    def process(cls, cls_name: str = ""):
        if not cls_name:
            cls.process_all()
            return

        cls.process_single(cls_name)

    @classmethod
    def process_single(cls, cls_name: str):
        processors = {c.__name__: c for c in cls.processors}
        processor = processors.get(cls_name)
        if not processor:
            print(f'No processor named "{cls_name}" was found.')
            return
        cls.process_all([processor])

    @classmethod
    def process_all(cls, processors: list[Type[JobProcessor]] = None):
        """
        Runs a list of information parsers through all
        of the jobs.
        """

        from job.models import Job

        jobs: list[Job] = list(Job.objects.all())
        fields_to_update: list[str] = []
        processors = processors or cls.processors

        for processor in processors:
            print(f'Processing data with "{processor.__name__}"')
            start = perf_counter()
            processor.process(jobs)
            print(f"Time: {perf_counter() - start:.4f} secs")
            fields_to_update.extend(processor.fields)

        print(f"{fields_to_update = }")

        if fields_to_update:
            Job.objects.bulk_update(
                jobs,
                fields=fields_to_update,
                batch_size=100,
            )
