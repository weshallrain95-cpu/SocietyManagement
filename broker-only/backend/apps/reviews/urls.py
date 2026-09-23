from django.urls import path

from . import api

urlpatterns = [
    path("brokers/<uuid:pk>/reviews", api.BrokerReviews.as_view()),
    path("interactions/<uuid:pk>/reviews", api.InteractionReview.as_view()),
    path("public/reviews/<str:token>", api.PublicReview.as_view()),
]
