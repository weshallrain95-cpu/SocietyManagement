from django.urls import path

from . import views

urlpatterns = [
    path("c/<str:token>", views.confirm_status, name="link-confirm"),
    path("o/<str:token>", views.visit_notice, name="link-visit-notice"),
    path("s/<str:token>", views.shortlist, name="link-shortlist"),
    path("v/<str:token>", views.visit_plan, name="link-visit-plan"),
    path("consent/<str:token>", views.consent, name="link-consent"),
    path("r/<str:token>", views.review, name="link-review"),
]
