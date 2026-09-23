from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from common import crypto
from common.ids import uuid7
from common.models import BaseModel


class UserManager(BaseUserManager):
    def get_by_phone(self, phone: str):
        return self.get(phone_hash=crypto.phone_hash(crypto.normalise_phone(phone)))

    def create_user(self, phone: str, display_name: str = "", password=None, **extra):
        e164 = crypto.normalise_phone(phone)
        user = self.model(phone_hash=crypto.phone_hash(e164), phone_enc=crypto.encrypt(e164), display_name=display_name, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone: str, password: str, **extra):
        return self.create_user(phone, password=password, is_staff=True, is_superuser=True, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    """A person. Phone is the identity; it is stored encrypted plus an HMAC for lookup."""

    class Status(models.TextChoices):
        ACTIVE = "active"
        SUSPENDED = "suspended"
        DELETED = "deleted"

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    phone_hash = models.CharField(max_length=64, unique=True)
    phone_enc = models.BinaryField()
    display_name = models.CharField(max_length=120, blank=True)
    email_enc = models.BinaryField(null=True, blank=True)
    preferred_lang = models.CharField(max_length=5, default="en")
    trust_score = models.PositiveSmallIntegerField(default=50)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "phone_hash"
    REQUIRED_FIELDS: list[str] = []
    objects = UserManager()

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def phone(self) -> str:
        return crypto.decrypt(self.phone_enc)

    def __str__(self):
        return self.display_name or crypto.mask_phone(self.phone)


class OtpChallenge(BaseModel):
    phone_hash = models.CharField(max_length=64, db_index=True)
    code_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    consumed_at = models.DateTimeField(null=True, blank=True)
    purpose = models.CharField(max_length=20, default="login")


class Consent(BaseModel):
    class Purpose(models.TextChoices):
        MARKETING = "marketing"
        SHARE_CONTACT = "share_contact_with_broker"
        LOCATION = "location_tracking"
        WHATSAPP = "whatsapp"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="consents")
    purpose = models.CharField(max_length=40, choices=Purpose.choices)
    version = models.CharField(max_length=20, default="2026-09")
    granted_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
