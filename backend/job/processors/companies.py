from django.utils.text import slugify

from .types import JobProcessor


class CompanyAliasProcessor(JobProcessor):
    """
    Creates CompanyName rows from jobs.
    """

    fields = ["company_name_id"]

    @staticmethod
    def process(jobs: list):
        from job.models import CompanyName, Job

        slug_names: dict[str, str] = {}

        job: Job
        for job in jobs:
            name = job.info_model().job.company
            slug = slugify(name)
            slug_names[slug] = name
            job.company_name_id = slug

        CompanyName.objects.bulk_create(
            [CompanyName(name=name, slug=slug) for slug, name in slug_names.items()],
            ignore_conflicts=True,
        )


class CompanyProcessor(JobProcessor):
    fields: list[str] = []

    @staticmethod
    def process(jobs: list):
        ...
