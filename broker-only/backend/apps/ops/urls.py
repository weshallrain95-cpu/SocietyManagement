from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("login", views.Login.as_view(), name="ops-login"),
    path("logout", auth_views.LogoutView.as_view(next_page="ops-login"), name="ops-logout"),
    path("", views.dashboard, name="ops-home"),
    path("brokers", views.brokers, name="ops-brokers"),
    path("brokers/<uuid:pk>/decide", views.broker_decide, name="ops-broker-decide"),
    path("queue", views.queue, name="ops-queue"),
    path("queue/<uuid:pk>", views.queue_act, name="ops-queue-act"),
    path("societies", views.societies, name="ops-societies"),
    path("societies/<uuid:pk>", views.society, name="ops-society"),
    path("map", views.pin_map, name="ops-map"),
    path("registers", views.registers, name="ops-registers"),
    path("audit", views.audit_view, name="ops-audit"),
]
