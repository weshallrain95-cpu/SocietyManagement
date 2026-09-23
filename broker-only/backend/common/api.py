"""Shared API helpers."""

from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

from .links import LinkError


class Paginated(CursorPagination):
    ordering = "-created_at"
    page_size = 50


class Gone(APIException):
    status_code = 410
    default_detail = "This link is no longer valid."


class DomainError(APIException):
    status_code = 400


def domain_call(fn, *args, **kwargs):
    """Run a service call, turning known domain errors into clean 400/410 responses."""
    try:
        return fn(*args, **kwargs)
    except LinkError as e:
        raise Gone(str(e)) from e
    except (ValueError, PermissionError) as e:
        raise DomainError(str(e)) from e
    except Exception as e:  # noqa: BLE001
        if e.__class__.__name__.endswith("Error") and e.__class__.__module__.startswith("apps."):
            raise DomainError(str(e)) from e
        raise


class PublicLinkThrottle(AnonRateThrottle):
    scope = "public_link"


class PublicLinkMixin:
    """Endpoints opened from WhatsApp/SMS links by people without accounts."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes = [PublicLinkThrottle]


class LatLng(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)


def is_field_staff(request) -> bool:
    m = getattr(request.user, "active_membership", None)
    return bool(m) and m.role == "broker_staff"
