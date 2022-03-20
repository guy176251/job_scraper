import os
import pickle

from .types import JobProcessor

FILE_NAME = "info.pickle"


class BackupProcessor(JobProcessor):
    """
    Backs up info jsons to pickle file.
    Stores them in a single dict with job keys
    mapped to an info json.
    """

    fields: list[str] = []

    @staticmethod
    def process(jobs: list):
        from job.models import Job

        infos: dict[str, dict] = {}

        try:
            with open(FILE_NAME, "rb") as f:
                temp = pickle.load(f)
        except FileNotFoundError:
            pass
        else:
            infos.update(temp)

        job: Job
        for job in jobs:
            infos[job.key] = job.info

        with open(FILE_NAME, "wb") as f:
            pickle.dump(infos, f)

    @staticmethod
    def restore():
        from job.models import Job

        try:
            with open(FILE_NAME, "rb") as f:
                infos = pickle.load(f)
        except FileNotFoundError:
            print(f'"{FILE_NAME}" does not exist in "{os.getcwd()}"')
            return

        assert type(infos) == dict

        jobs = [Job(key=key, info=info) for key, info in infos.items()]

        if jobs:
            Job.objects.bulk_create(jobs, ignore_conflicts=True)
