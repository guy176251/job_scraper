import itertools
from base64 import b64decode
from time import sleep
from typing import Optional

import httpx
from bs4 import BeautifulSoup as Soup
from bs4 import ResultSet, Tag
from django.core.management.base import BaseCommand

from apply.models import Application
from job.models import Job
from job.processors import MainProcessor

REQUEST_SLEEP = 1.5
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
HEADERS = {"user-agent": USER_AGENT}
SEARCHES = [
    "python developer",
    "django developer",
    "backend developer",
    "junior developer",
    "entry level developer",
    "flask developer",
    "web scraping developer",
    "typescript developer",
    "react developer",
    "java developer",
    "c# developer",
    "elixir developer",
]

LOCATIONS = [
    "Remote",
    "Houston, TX",
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        scrape_jobs()
        MainProcessor.process()
        Application.objects.bulk_create_applications()


class JobScraper:
    @staticmethod
    def key(job: Tag) -> str:
        return job.select_one(".SerpJob-link")["href"][5:59].strip()

    @staticmethod
    def elems(soup: Soup) -> ResultSet:
        return soup.select(".SerpJob")

    @staticmethod
    def pages(soup: Soup) -> ResultSet:
        return soup.select(".Pagination-link")


class CustomClient(httpx.Client):
    API = b64decode(
        "aHR0cHM6Ly93d3cuc2ltcGx5aGlyZWQuY29tL2FwaS9qb2I=".encode()
    ).decode()
    SEARCH = b64decode(
        "aHR0cHM6Ly93d3cuc2ltcGx5aGlyZWQuY29tL3NlYXJjaA==".encode()
    ).decode()

    def rate_limited_get(self, *args, **kwargs):
        resp = self.get(*args, **kwargs)
        sleep(REQUEST_SLEEP)
        return resp

    def get_job_info(self, key: str) -> Optional[dict]:
        resp = self.rate_limited_get(
            self.API,
            params={"key": key},
            cookies=httpx.Cookies(),
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Status: {resp.status_code}")
            return None

    def get_search_page(
        self,
        search: str,
        location: str,
        page_num: int = 1,
    ) -> Optional[Soup]:
        resp = self.rate_limited_get(
            self.SEARCH,
            params={
                "q": search,
                "pn": page_num,
                "l": location,
            },
            cookies=httpx.Cookies(),
        )
        if resp.status_code == 200:
            print("Got search page")
            return Soup(resp.text, "lxml")
        else:
            print(f"Status: {resp.status_code}")
            return None


def scrape_jobs():
    client = CustomClient(headers=HEADERS)

    jobs: list[Job] = []
    search_pages: list[Soup] = []

    for search, location in itertools.product(SEARCHES, LOCATIONS):

        print(f'Job search: "{search}" in "{location}"')
        page = client.get_search_page(
            search=search,
            page_num=1,
            location=location,
        )
        search_pages.append(page)
        page_count = len(JobScraper.pages(page))

        for page_num in range(2, page_count + 1):
            search_pages.append(
                client.get_search_page(
                    search=search,
                    page_num=page_num,
                    location=location,
                )
            )

        for page in search_pages:
            if not page:
                continue

            jobs.extend(
                Job(key=JobScraper.key(job)) for job in JobScraper.elems(page)
            )

    prev_jobs = set(Job.objects.values_list("key", flat=True))
    jobs = list(
        {job.key: job for job in jobs if job.key not in prev_jobs}.values()
    )

    print(f"Getting {len(jobs)} jobs")
    for index, job in enumerate(jobs):
        info = client.get_job_info(key=job.key)
        if info:
            job.info = info
            print(
                f'{int((index + 1) / len(jobs) * 100)}% | Got job "{job.key}"'
            )

    print("Saving jobs")
    Job.objects.bulk_create(jobs, ignore_conflicts=True)
