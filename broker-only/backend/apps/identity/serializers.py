from rest_framework import serializers

from common import crypto


class PhoneField(serializers.CharField):
    def to_internal_value(self, data):
        try:
            return crypto.normalise_phone(super().to_internal_value(data))
        except ValueError as e:
            raise serializers.ValidationError(str(e)) from e


class OtpRequestSerializer(serializers.Serializer):
    phone = PhoneField()


class OtpVerifySerializer(serializers.Serializer):
    phone = PhoneField()
    code = serializers.RegexField(r"^\d{6}$")
    display_name = serializers.CharField(required=False, allow_blank=True, max_length=120)


class SwitchRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["customer", "broker", "owner"])
    org_id = serializers.UUIDField(required=False)


class MeSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    display_name = serializers.CharField(max_length=120, required=False)
    preferred_lang = serializers.ChoiceField(choices=["en", "hi", "mr"], required=False)
    phone_masked = serializers.SerializerMethodField()
    memberships = serializers.SerializerMethodField()
    active_role = serializers.SerializerMethodField()
    active_org_id = serializers.SerializerMethodField()

    def get_phone_masked(self, user):
        return crypto.mask_phone(user.phone)

    def get_memberships(self, user):
        return [
            {"org_id": str(m.org_id), "org_name": m.org.name, "role": m.role, "can": m.effective_permissions()}
            for m in user.memberships.filter(active=True).select_related("org")
        ]

    def get_active_role(self, user):
        return getattr(user, "active_role", "customer")

    def get_active_org_id(self, user):
        org = getattr(user, "active_org_id", None)
        return str(org) if org else None
