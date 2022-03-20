# from devtools import debug
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponseRedirect, QueryDict
from django.shortcuts import render
from ninja import Form, Query, Router, Schema

from .forms import AppForm, CompanyForm, SearchForm
from .models import Application, CompanyName, Job

job_router = Router()


class SearchBarData(Schema):
    apply: str = ""
    indeed: bool | None = None
    location: str = ""
    regex: bool = False
    search: str = ""
    min_years: int = 0


@job_router.get("", url_name="job-list")
def list_jobs(
    request: HttpRequest,
    blocked: bool = False,
    page: int = 1,
    searchbar: SearchBarData = Query(...),
):
    jobs = Job.objects.outgoing(
        search=searchbar.search,
        apply=searchbar.apply,
        regex=searchbar.regex,
        location=searchbar.location,
        indeed=searchbar.indeed,
        blocked=blocked,
        min_years=searchbar.min_years,
    )
    paginator = Paginator(jobs, 50)
    paginated_jobs = paginator.page(page)

    # wyling manual pagination shit
    q = QueryDict(mutable=True)
    q.update(request.GET)
    pagination_links: list[tuple[int, str]] = []
    for num in paginator.page_range:
        q["page"] = num
        pagination_links.append((num, f"{request.path}?{q.urlencode()}"))

    return render(
        request,
        "list.html",
        context={
            "page_num": page,
            "job_count": jobs.count(),
            "pagination_links": pagination_links,
            "jobs": paginated_jobs,
            "apply": searchbar.apply,
            "search": searchbar.search,
            "indeed": searchbar.indeed,
            "searchbar": SearchForm.from_search(
                search=searchbar.search,
                apply=searchbar.apply,
            ),
        },
    )


@job_router.get("job/{slug:key}", url_name="job-detail")
def get_job(request, key: str):
    job = Job.objects.get(pk=key)

    return render(
        request,
        "detail.html",
        context={
            "job": job,
            "app_form": AppForm.from_job(
                job=job,
                redirect=request.path,
            ),
            "company_form": CompanyForm({"redirect": request.path}),
        },
    )


class AppFormData(Schema):
    notes: str = ""
    is_applying: str = ""
    redirect: str


@job_router.post("job/{slug:key}/notes", url_name="update-application")
def update_application(
    request: HttpRequest,
    key: str,
    form: AppFormData = Form(...),
):
    Application.objects.filter(pk=key).update(
        notes=form.notes,
        is_applying=form.is_applying,
    )

    return HttpResponseRedirect(form.redirect)


class KeywordFormData(Schema):
    keywords: str = ""
    redirect: str


@job_router.post("job/{slug:key}/keywords", url_name="update-keywords")
def update_keywords(
    request,
    key: str,
    form: KeywordFormData = Form(...),
):
    Job.objects.update_keywords(pk=key, keyword_string=form.keywords)
    return HttpResponseRedirect(form.redirect)


class CompanyFormData(Schema):
    blocked: bool
    redirect: str


@job_router.post("company/{slug:slug}", url_name="update-company")
def update_company(
    request: HttpRequest,
    slug: str,
    form: CompanyFormData = Form(...),
):
    CompanyName.objects.filter(slug=slug).update(blocked=form.blocked)
    return HttpResponseRedirect(form.redirect)


# def page_view(request, page, apply="new"):
#     """
#     Page number is 1-indexed.
#     """
#
#     jobs = get_jobs(request, apply)
#
#     job: Job
#     try:
#         job = jobs[page - 1]
#     except IndexError:
#         job = jobs[0]
#         page = 1
#
#     pagination = {
#         "redirect": max(page - 1, 1),
#         "next": page + 1,
#         "current": page,
#         "last": Job.objects.get_local_results().count() - 1,
#     }
#
#     return render(
#         request,
#         "paginated.html",
#         context={
#             "job": job,
#             "apply": apply,
#             **forms(job),
#             **pagination,
#         },
#     )
