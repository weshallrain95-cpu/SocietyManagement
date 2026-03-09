# statutory/urls.py — LIFECYCLE ROUTER

from django.urls import path

from statutory.api import (
    preregistration_snapshot_view,
    update_preregistration_obligation_status,
    upload_preregistration_document,
    delete_preregistration_document,
    societies_list_view,
    registrar_pack_view,
    registrar_pack_download_view,
    submit_to_registrar,
)

urlpatterns = [

    # Society listing
    path(
        "societies/",
        societies_list_view,
        name="societies-list",
    ),

    # Preregistration snapshot
    path(
        "societies/<int:society_id>/preregistration/snapshot/",
        preregistration_snapshot_view,
        name="preregistration-snapshot",
    ),

    # Obligation status update
    path(
        "preregistration/obligations/<int:obligation_id>/status/",
        update_preregistration_obligation_status,
        name="update-preregistration-obligation-status",
    ),

    # Document upload/delete
    path(
        "preregistration/documents/upload/",
        upload_preregistration_document,
        name="upload-preregistration-document",
    ),
    path(
        "preregistration/documents/delete/",
        delete_preregistration_document,
        name="delete-preregistration-document",
    ),

    # Registrar pack
    path(
        "societies/<int:society_id>/registrar-pack/",
        registrar_pack_view,
        name="registrar-pack",
    ),
    path(
        "societies/<int:society_id>/registrar-pack/download/",
        registrar_pack_download_view,
        name="registrar-pack-download",
    ),
    path(
        "societies/<int:society_id>/submit/",
        submit_to_registrar,
        name="submit-to-registrar",
    ),
]

from statutory.cockpit import preregistration_cockpit_view

urlpatterns += [
    path(
        "preregistration/cockpit/<int:society_id>/",
        preregistration_cockpit_view,
        name="preregistration-cockpit",
    ),

    path(
        "societies/<int:society_id>/cockpit/",
        preregistration_cockpit_view,
        name="society-cockpit",
    ),
]

from statutory.api import control_room_overview

urlpatterns += [
    path(
        "control-room/overview/",
        control_room_overview,
        name="control-room-overview",
    ),
]
