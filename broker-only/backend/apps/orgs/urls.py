from django.urls import path

from . import views

urlpatterns = [
    path("broker-orgs", views.BrokerOrgCreateView.as_view()),
    path("broker-orgs/me", views.MyOrgView.as_view()),
    path("broker-orgs/me/staff", views.StaffView.as_view()),
    path("broker-orgs/me/staff/<uuid:membership_id>", views.StaffRemoveView.as_view()),
    path("broker-orgs/me/staff/<uuid:membership_id>/permissions", views.MemberPermissionsView.as_view()),
    path("broker-orgs/me/service-areas", views.ServiceAreaListCreate.as_view()),
    path("broker-orgs/me/service-areas/<uuid:pk>", views.ServiceAreaDelete.as_view()),
    path("brokers/<uuid:pk>", views.PublicBrokerView.as_view()),
    path("admin-api/verifications", views.VerificationQueueView.as_view()),
    path("admin-api/verifications/<uuid:org_id>", views.VerificationDecisionView.as_view()),
]
