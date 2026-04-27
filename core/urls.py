# core/urls.py — AUTHORITATIVE ROOT ROUTER

from django.contrib import admin
from django.urls import path, include
from core import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Admin
    path("admin/", admin.site.urls),

    # Core UI lifecycle entry
    path("", views.case_create, name="case_create"),
    path("case/<int:case_id>/", views.case_dashboard, name="case_dashboard"),

    # Stage navigation
    path(
        "case/<int:case_id>/stage/<str:stage_code>/",
        views.stage_entry,
        name="stage_entry",
    ),
    path(
        "case/<int:case_id>/stage/<str:stage_code>/checklist/",
        views.stage_checklist,
        name="stage_checklist",
    ),
    path(
        "case/<int:case_id>/stage/<str:stage_code>/decisions/",
        views.decision_workspace,
        name="decision_workspace",
    ),

    # API domains (ONLY includes allowed below)
    path("api/society/", include("society.api.urls")),
    path("api/statutory/", include("statutory.urls")),
    path("api/bylaws/", include("bylaws.urls")),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)