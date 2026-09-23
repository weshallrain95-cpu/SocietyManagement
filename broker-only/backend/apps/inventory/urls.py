from django.urls import path

from . import api

urlpatterns = [
    path("listings", api.ListingListCreate.as_view()),
    path("listings/<uuid:pk>", api.ListingDetail.as_view()),
    path("listings/<uuid:pk>/status", api.ListingStatusView.as_view()),
    path("listings/<uuid:pk>/reconfirm", api.ListingReconfirmView.as_view()),
    path("listings/<uuid:pk>/keys", api.KeysView.as_view()),
    path("listings/<uuid:pk>/copy-attributes", api.CopyAttributesView.as_view()),
    path("uploads", api.UploadCreateView.as_view()),
    path("uploads/template", api.UploadTemplateView.as_view()),
    path("uploads/<uuid:pk>", api.UploadDetailView.as_view()),
    path("uploads/<uuid:pk>/rows", api.UploadRowsView.as_view()),
    path("uploads/<uuid:pk>/rows/<uuid:row_id>/resolve", api.UploadRowResolveView.as_view()),
    path("uploads/<uuid:pk>/commit", api.UploadCommitView.as_view()),
]
