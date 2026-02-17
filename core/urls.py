"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

from statutory.api import (
    next_legal_step,
    complete_legal_step,
    finalize_society_completion,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/society/<int:society_id>/next-step/",
        next_legal_step,
    ),

    path(
        "api/society/<int:society_id>/complete-step/",
        complete_legal_step,
    ),

    path(
        "api/society/<int:society_id>/finalize/",
        finalize_society_completion,
    ),
]
from django.urls import path, include

urlpatterns += [
    path("api/", include("society.api.urls")),
]

from django.urls import include, path

urlpatterns = [
    # ... existing routes
    path("", include("statutory.urls")),
]

from statutory.bylaws.api import full_bylaw_version

urlpatterns += [
    path("api/bylaws/<str:code>/full/", full_bylaw_version),
]

from django.urls import path
from statutory.bylaws.views import BylawsVersionExportView

urlpatterns += [
    path("api/bylaws/version/<str:code>/export/", BylawsVersionExportView.as_view(), name="bylaws-version-export"),
]

from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("bylaws/", include("statutory.bylaws.urls")),
]

from django.urls import path
from .views import status_selection
from . import views

urlpatterns = [
    path("", status_selection, name="status_selection"),
    path("start/", views.case_initiation, name="case_initiation"),
    path("case/create/", views.case_create, name="case_create"),
    path("case/<int:case_id>/", views.case_dashboard, name="case_dashboard"),
]


