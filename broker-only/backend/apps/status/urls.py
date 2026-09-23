from django.urls import path

from . import api

urlpatterns = [path("public/confirmations/<str:token>", api.PublicConfirmationView.as_view())]
