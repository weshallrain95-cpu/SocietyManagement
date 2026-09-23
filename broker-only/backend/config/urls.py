from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.audit.views import VerifyAuditView


def health(_request):
    return JsonResponse({"ok": True})


urlpatterns = [
    path("health", health),
    path("django-admin/", admin.site.urls),
    path("v1/schema", SpectacularAPIView.as_view(), name="schema"),
    path("v1/docs", SpectacularSwaggerView.as_view(url_name="schema")),
    path("v1/admin-api/audit/verify", VerifyAuditView.as_view()),
    path("ops/", include("apps.ops.urls")),
    path("", include("apps.linkpages.urls")),
    *[
        path("v1/", include(f"apps.{app}.urls"))
        for app in (
            "identity",
            "orgs",
            "masterdata",
            "inventory",
            "status",
            "crm",
            "visits",
            "marketplace",
            "reviews",
        )
    ],
]
