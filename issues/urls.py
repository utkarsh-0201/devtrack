from django.urls import path

from .views import IssueView, ReporterView

app_name = "issues"  # enables namespaced URL reversals, e.g. reverse("issues:list")

urlpatterns = [
    # ---------------------------------------------------------------------
    # /api/issues/
    #
    # GET  — returns all issues, or a subset when query params are supplied:
    #          ?id=<int>       → single issue by ID
    #          ?status=<str>   → issues filtered by status
    #
    # POST — creates a new issue from a JSON request body.
    #        Required field : title (str)
    #        Optional fields: description (str), status (str),
    #                         reported_by (str)
    # ---------------------------------------------------------------------
    path(
        "issues/",
        IssueView.as_view(),
        name="issue-list-create",
    ),
    path(
        "reporters/",
        ReporterView.as_view(),
        name="reporter-list-create",
    ),
]