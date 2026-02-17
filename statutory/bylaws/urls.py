from django.urls import path
from .views import bylaws_viewer

urlpatterns = [
    path("", bylaws_viewer, name="bylaws_viewer"),
    path("step-2/", bylaws_viewer),  # temporary placeholder
]

from django.urls import path
from . import views

urlpatterns = [
    path("start/<int:case_id>/", views.start_bylaws_engine),
    path("draft/<int:draft_id>/", views.bylaws_draft_workspace),
]
