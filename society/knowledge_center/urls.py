from django.urls import path

from .views import knowledge_center


urlpatterns = [

    path(
        "",
        knowledge_center,
        name="knowledge-center",
    ),

]