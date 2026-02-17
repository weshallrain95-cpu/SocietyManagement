from django.urls import path

from statutory.api import (
    preregistration_snapshot_view,
    update_preregistration_obligation_status,
    upload_preregistration_document,
    delete_preregistration_document,
    societies_list_view,
    registrar_pack_view,
    registrar_pack_download_view,
)

urlpatterns = [
    path(
        "api/societies",
        societies_list_view,
        name="societies-list",
    ),

    path(
        "api/societies/<int:society_id>/preregistration/snapshot",
        preregistration_snapshot_view,
        name="preregistration-snapshot",
    ),

    path(
        "api/preregistration/obligations/<int:obligation_id>/status",
        update_preregistration_obligation_status,
        name="update-preregistration-obligation-status",
    ),

    path(
        "api/preregistration/documents/upload",
        upload_preregistration_document,
        name="upload-preregistration-document",
    ),

    path(
        "api/societies/<int:society_id>/registrar-pack",
        registrar_pack_view,
        name="registrar-pack",
    ),

    path(
        "api/preregistration/documents/delete",
        delete_preregistration_document,
        name="delete-preregistration-document",
    ),

    path(
        "api/societies/<int:society_id>/registrar-pack/download",
        registrar_pack_download_view,
    ),

]

from statutory.bylaws.api import (
    list_bylaw_decisions,
    save_bylaw_decisions,
)

urlpatterns += [
    path("api/bylaws/decisions", list_bylaw_decisions),
    path("api/societies/<int:society_id>/bylaws/decisions/save", save_bylaw_decisions),
]
