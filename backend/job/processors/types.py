from abc import ABC, abstractmethod


class JobProcessor(ABC):
    """
    Represents a job processor, which contains a method
    that adds info to each job in a list of jobs, and a
    list of database field names that are to be updated.
    """

    fields: list[str]

    @staticmethod
    @abstractmethod
    def process(jobs: list):
        ...
