from django.urls import path

from . import api

urlpatterns = [
    path("visit-plans", api.PlanListCreate.as_view()),
    path("visit-plans/<uuid:pk>", api.PlanDetail.as_view()),
    path("visit-plans/<uuid:pk>/stops/<uuid:stop_id>", api.StopRemove.as_view()),
    path("visit-plans/<uuid:pk>/<slug:action>", api.PlanAction.as_view()),
    path("visit-stops/<uuid:pk>/checkin", api.StopCheckin.as_view()),
    path("visit-stops/<uuid:pk>/outcome", api.StopOutcome.as_view()),
    path("sync", api.SyncView.as_view()),
    path("public/visit-plans/<str:token>", api.PublicPlanView.as_view()),
    path("public/visit-notices/<str:token>", api.PublicVisitNoticeView.as_view()),
]
