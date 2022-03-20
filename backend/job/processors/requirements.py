import re
from functools import reduce
from typing import Optional, Type

from markdownify import markdownify as md
from pydantic import BaseModel, validator

from .types import JobProcessor


class RequirementProcessor(JobProcessor):
    """
    Get year requirements from markdown-converted job descriptions.

    Look for matches in order of match specificity,
    i.e. OpenEnded is less specific than FromTo etc.

    Then, store those matches as a key-pair with the description
    line being the key and the match being the value. This way,
    we can retain only the most specific match for said line.
    """

    fields = ["requirements", "requirement_years"]

    @staticmethod
    def process(jobs: list):
        from job.models import Job

        parsers: list[Type[Parser]] = [
            OpenEnded,
            FromTo,
            Required,
        ]

        job: Job
        for job in jobs:
            description = job.info_model().job.description
            lines: dict[str, Parser] = {}

            for parser in parsers:
                requirements = parser.from_description(description)
                for requirement in requirements:
                    lines[requirement.string] = requirement

            job.requirement_years = reduce(
                lambda prev, req: prev + req.years, lines.values(), 0
            )
            job.requirements = [o.dict() for o in lines.values()] or None


class Parser(BaseModel):
    """
    Parses year requirements from a job.
    """

    _regex: str
    years: int
    string: str

    @validator("years")
    def max_years(cls, value: int):
        if value > 10:
            raise ValueError("too big")
        return value

    @validator("string")
    def remove_stars(cls, value: str):
        return value.replace("*", "")

    @classmethod
    def from_description(cls, description: str) -> list["Parser"]:
        description_lines = md(description).splitlines()
        requirements: list["Parser"] = []

        for line in description_lines:
            requirement = cls.from_line(line)
            if requirement:
                requirements.append(requirement)

        return requirements

    @classmethod
    def from_line(cls, line: str) -> Optional["Parser"]:
        """
        Should parse string with `self._regex` and return instance.
        """
        if not cls.line_is_valid(line):
            return None

        match = re.search(cls._regex, line, flags=re.IGNORECASE)
        if match is None:
            return None

        years = match.groupdict()["years"]
        return cls.valid_or_none(years=years, string=line)

    @classmethod
    def line_is_valid(cls, line: str) -> bool:
        """
        Performs preliminary check on string before doing regex check.
        Defaults to always returning True.
        """
        return True

    @classmethod
    def valid_or_none(cls, *args, **kwargs):
        try:
            return cls(*args, **kwargs)
        except ValueError:
            return None


class OpenEnded(Parser):
    """Represents an open-ended requirement match."""

    _regex: str = r"(?P<years>\d+).*year"

    @classmethod
    def line_is_valid(cls, line: str) -> bool:
        regex = r"\$|\%|usd"
        return not (len(line) > 200 or re.search(regex, line, flags=re.IGNORECASE))


class FromTo(Parser):
    """
    Represents a contrained requirement match.
    `years` represents the low end of the year requirement.
    """

    # _regex: str = r"(?P<low>\d+)\s*(-|to|–)\s*(?P<high>\d+)\s+year"
    _regex: str = r"(?P<years>\d+)\s*(-|to|–)\s*\d+\s+year"


class Required(Parser):
    """Represents a detailed requirement match."""

    # _regex: str = (
    #     r"\* (?P<tech>.*):\s+(?P<years>\d+)\s+years?\s+\((?P<required>\w+)\)"
    # )
    _regex: str = r"\* (.*):\s+(?P<years>\d+)\s+years?\s+\(\w+\)"
