from django.contrib.auth.backends import ModelBackend

from common import crypto

from .models import User


class PhoneBackend(ModelBackend):
    """Lets platform staff log in to the Django admin with phone + password."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(phone_hash=crypto.phone_hash(crypto.normalise_phone(username or "")))
        except (ValueError, User.DoesNotExist):
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
