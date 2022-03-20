from django.urls import path

from job import views

urlpatterns = [
    # path("", views.list_view, name="job-list"),
    # path("page/<int:page>", views.page_view, name="job-detail-paginated"),
    # path("apply/<slug:apply>", views.list_view, name="job-apply-list"),
    # path(
    #     "apply/<slug:apply>/page/<int:page>",
    #     views.page_view,
    #     name="job-apply-detail",
    # ),
    # path("job/<slug:key>/notes", views.update_application, name="update-notes"),
    # path(
    #     "job/<slug:key>/keywords",
    #     views.update_keywords,
    #     name="update-keywords",
    # ),
    # path("job/<slug:key>", views.detail_view, name="job-detail"),
    # *views.job_router.urls[0],
]
