from django.urls import path

from . import api

urlpatterns = [
    path("localities", api.LocalityListView.as_view()),
    path("societies/search", api.SocietySearchView.as_view()),
    path("societies/proposals", api.ProposeSocietyView.as_view()),
    path("societies/<uuid:pk>", api.SocietyDetailView.as_view()),
    path("societies/<uuid:pk>/check-flat", api.CheckFlatView.as_view()),
    path("buildings/<uuid:pk>/units", api.BuildingUnitsView.as_view()),
    path("buildings/<uuid:pk>/layout-report", api.LayoutReportView.as_view()),
    path("units/<uuid:pk>", api.UnitCardView.as_view()),
    path("units/<uuid:pk>/attribute-suggestions", api.AttributeSuggestionView.as_view()),
    path("attributes/dictionary", api.DictionaryView.as_view()),
    path("admin-api/queue", api.AdminQueueView.as_view()),
    path("admin-api/queue/<uuid:pk>/resolve", api.AdminQueueResolveView.as_view()),
    path("admin-api/societies/<uuid:pk>/merge", api.AdminMergeView.as_view()),
    path("admin-api/societies/<uuid:pk>/approve", api.AdminApproveSocietyView.as_view()),
]
