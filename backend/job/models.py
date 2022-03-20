import operator
from datetime import datetime, timedelta
from functools import reduce
from typing import Any

from django.db import models
from django.db.models import OuterRef, Q, Subquery
from django.db.models.functions import Length
from django.utils.functional import cached_property
from django.utils.text import slugify
from markdownify import markdownify as md
from sql_util.utils import Exists

from apply.models import Application

from .processors import Info

models.TextField.register_lookup(Length)


class ModelNames:
    COMPANY = "Company"
    COMPANY_ALIAS = "CompanyName"
    JOB = "Job"


class Job(models.Model):

    LOCATIONS = ["Remote", "Houston, TX"]
    LOCATION_CHOICES = [(location, location) for location in LOCATIONS]

    key: models.CharField = models.CharField(max_length=60, primary_key=True)
    info = models.JSONField()

    # app facing fields
    rating: models.DecimalField = models.DecimalField(
        decimal_places=1, max_digits=2, null=True
    )
    keywords = models.JSONField(null=True)
    skills = models.JSONField(null=True)

    description: models.TextField = models.TextField(null=True)
    location: models.TextField = models.TextField(null=True)
    title: models.TextField = models.TextField(null=True)

    hash: models.BinaryField = models.BinaryField(null=True)
    created_on: models.DateTimeField = models.DateTimeField(null=True)

    requirements = models.JSONField(null=True)
    requirement_years: models.IntegerField = models.IntegerField(null=True)

    company_name: models.ForeignKey = models.ForeignKey(
        ModelNames.COMPANY_ALIAS,
        on_delete=models.SET_NULL,
        null=True,
        related_name="jobs",
    )
    company: models.ForeignKey = models.ForeignKey(
        ModelNames.COMPANY,
        on_delete=models.SET_NULL,
        null=True,
        related_name="jobs",
    )

    @cached_property
    def pretty_description(self):
        return md(self.description)

    @cached_property
    def keyword_string(self) -> str:
        return "\n".join(self.keywords) if self.keywords else ""

    def info_model(self) -> Info:
        return Info(**self.info)

    def create_application(self):
        """
        Creates Application for job object. Should
        only be run through post-create signal.
        """

        if self.application:
            return

        application = Application.objects.filter(pk=self.key).first()
        if application is None:
            Application.objects.create(job_key=self.key)

    @cached_property
    def application(self):
        return Application.objects.get(pk=self.key)

    class Meta:
        ordering = [
            "requirement_years",
            "-info__job__indeedApply",
            "-created_on",
            "description__length",
        ]

    class QuerySet(models.QuerySet):
        def base_filter(self):
            """
            Filters out things that shouldn't be in any queryset.
            """

            in_local_area = Q(location__in=self.model.LOCATIONS)

            now = datetime.now()
            half_year = timedelta(weeks=26)
            half_year_old = Q(created_on__gte=now - half_year)

            not_senior = (
                ~Q(title__icontains="senior")
                & ~Q(title__icontains="sr.")
                & ~Q(title__icontains="lead")
                & ~Q(title__icontains="principal")
            )

            return self.filter(
                in_local_area & half_year_old & not_senior
            ).select_related(
                "company_name",
            )

        def update_keywords(self, pk, keyword_string: str):
            return self.filter(pk=pk).update(
                keywords=[
                    t.strip()
                    for t in keyword_string.strip().splitlines()
                    if t.strip()
                ]
            )

        def get_applying(self, apply: str):
            """
            Filters local results by applying status.
            Passing None returns jobs with no applying status.
            """

            query = Q(is_applying=apply)
            if apply not in Application.APPLY_VALUES:
                query = Q(is_applying__isnull=True)

            application_keys = set(
                Application.objects.filter(query).values_list(
                    "job_key", flat=True
                )
            )

            return self.filter(key__in=application_keys)

        def get_search(self, search: str, regex: bool):
            if not search:
                return self

            if regex:
                return self.filter(
                    Q(title__iregex=search) | Q(description__iregex=search)
                )

            def query(keyword):
                return Q(title__icontains=keyword) | Q(
                    description__icontains=keyword
                )

            keywords = [s.strip() for s in search.strip().split()]
            queries = [
                ~(query(kw[1:])) if kw.startswith("-") else query(kw)
                for kw in keywords
            ]
            whole_query = reduce(operator.and_, queries[1:], queries[0])

            return self.filter(whole_query)

        def get_location(self, location: str):
            return self if not location else self.filter(location=location)

        def get_indeed_applies(self, indeed: bool | None):
            return (
                self
                if indeed is None
                else self.filter(info__job__indeedApply=indeed)
            )

        def get_unblocked(self, blocked: bool):
            return self.annotate(
                is_blocked=Exists("company_name", filter=Q(blocked=True))
            ).filter(is_blocked=blocked)

        def get_min_years(self, min_years: int):
            return (
                self
                if not min_years
                else self.filter(requirement_years__gte=min_years)
            )

        def outgoing(
            self,
            apply: str = "",
            blocked: bool = False,
            indeed: bool | None = None,
            location: str = "",
            regex: bool = False,
            search: str = "",
            min_years: int = 0,
        ):
            return (
                self.base_filter()
                .get_min_years(min_years)
                .get_unblocked(blocked)
                .get_applying(apply)
                .get_search(search, regex)
                .get_location(location)
                .get_indeed_applies(indeed)
            )

    objects: Any = QuerySet.as_manager()


class Company(models.Model):
    name: models.CharField = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


class CompanyName(models.Model):
    name: models.CharField = models.CharField(max_length=100)
    company: models.ForeignKey = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        related_name="aliases",
    )
    blocked: models.BooleanField = models.BooleanField(default=False)
    slug: models.SlugField = models.SlugField(primary_key=True)

    def __str__(self):
        return self.name

    def create_slug(self):
        self.slug = slugify(self.name)
        self.save()
