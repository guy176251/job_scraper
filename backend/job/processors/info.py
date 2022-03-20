from datetime import datetime
from typing import Any, Optional

import arrow
import brotlicffi
from pydantic import BaseModel, ValidationError, root_validator, validator

from .types import JobProcessor


class InfoProcessor(JobProcessor):
    """
    Processes basic string info that should have a database column.
    """

    fields = [
        "description",
        "title",
        "location",
        "skills",
        "created_on",
        "hash",
        "rating",
    ]

    @staticmethod
    def process(jobs: list):
        from job.models import Job

        job: Job
        for job in jobs:
            try:
                info = job.info_model()
            except ValidationError as err:
                print(f"{job}: {err}")
                continue

            job.description = info.job.description
            job.title = info.job.title
            job.location = info.job.location
            job.skills = info.skillEntities
            job.created_on = info.job.time

            if info.job.companyRating:
                job.rating = info.job.companyRating

            job.hash = brotlicffi.compress(job.description.encode())


class IndeedApplyAttributes(BaseModel):
    jobUrl: str
    label: str
    partnerapitoken: str
    partnermeta: str
    pingbackUrl: str

    apiToken: Optional[str]
    coverletter: Optional[str]
    email: Optional[str]
    finishAppUrl: Optional[str]
    jk: Optional[str]
    jobCompanyName: Optional[str]
    jobId: Optional[str]
    jobLocation: Optional[str]
    jobMeta: Optional[str]
    jobTitle: Optional[str]
    locale: Optional[str]
    name: Optional[str]
    partnersa: Optional[str]
    phone: Optional[str]
    postUrl: Optional[str]
    questions: Optional[str]
    resume: Optional[str]


class JobAPI(BaseModel):
    absoluteUrl: str
    company: str
    companyRating: float
    description: str
    indeedApply: bool
    jobType: str
    location: str
    signPhotoURL: str
    sponsored: bool
    storeNamePhotoURL: str
    time: datetime
    title: str
    url: str

    indeedApplyAttributes: Optional[IndeedApplyAttributes]
    logoUrl: Optional[str]

    @root_validator(pre=True)
    def check_indeed_is_empty(cls, values):
        indeed = values.get("indeedApplyAttributes")
        if indeed is not None and not indeed:
            values.pop("indeedApplyAttributes")
        return values

    @validator("time")
    def to_central_timezone(cls, value):
        return arrow.get(value).to("US/Central").datetime


class Info(BaseModel):
    applyButtonWithCustomizedDesign: bool
    applyNowLabel: str
    applyUrl: str
    benefitsLabel: str
    collapseJobDescriptionLabel: str
    copyLinkConfirmLabel: str
    copyLinkLabel: str
    country: str
    emailLinkLabel: str
    enableCompanyRating: bool
    expandJobDescriptionLabel: str
    jobDescriptionLabel: str
    jobDetailsLabel: str
    jobKey: str
    language: str
    loginButtonLabel: str
    loginHeaderLabel: str
    mdApplyUrl: str
    newTabLabel: str
    qualificationsLabel: str
    saveButtonLabel: str
    serpTrackingKey: str
    shareJobLabel: str
    showJsPhotos: bool
    showShareMenu: bool
    tk: str
    translations: str

    job: JobAPI

    benefitEntities: Optional[list]
    educationEntities: Optional[list]
    formattedAge: Optional[str]
    isSalaryEstimate: Optional[bool]
    logoUrl: Optional[str]
    preEmploymentEntities: Optional[list]
    salaryInfo: Optional[str]
    shiftEntities: Any
    showCommuteTime: Optional[bool]
    skillEntities: Optional[list]
