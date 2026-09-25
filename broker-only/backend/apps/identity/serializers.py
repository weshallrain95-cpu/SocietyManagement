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
    email = serializers.EmailField(required=False, allow_blank=True)
    profile = serializers.DictField(required=False)
    phone_masked = serializers.SerializerMethodField()
    memberships = serializers.SerializerMethodField()
    active_role = serializers.SerializerMethodField()
    active_org_id = serializers.SerializerMethodField()

    PROFILE = {
        "customer": {"intent": ("rent", "buy"), "move_in": ("now", "1-3m", "exploring"), "contact": ("call", "whatsapp")},
        "owner": {"flats": ("1", "2-3", "4+"), "plan": ("rent", "sell", "both", "records"), "contact": ("call", "whatsapp")},
    }

    def to_representation(self, user):
        d = super().to_representation(user)
        d["email"] = crypto.decrypt(user.email_enc) or "" if user.email_enc else ""
        d["profile"] = user.profile or {}
        return d

    def validate_profile(self, v):
        """Merge one mode's welcome answers into the stored profile; unknown keys and values are refused."""
        out = dict(getattr(self.instance, "profile", None) or {})
        for mode, answers in v.items():
            allowed = self.PROFILE.get(mode)
            if allowed is None or not isinstance(answers, dict):
                raise serializers.ValidationError(f"Unknown profile section: {mode}")
            clean = dict(out.get(mode) or {})
            for k, val in answers.items():
                if k == "areas" and mode == "customer":
                    clean[k] = [str(x) for x in val][:10] if isinstance(val, list) else []
                elif k == "welcomed" and val:
                    from django.utils import timezone

                    clean["welcomed_at"] = timezone.now().isoformat()
                elif k in allowed and val in allowed[k]:
                    clean[k] = val
                else:
                    raise serializers.ValidationError(f"{mode}.{k}: not a valid answer")
            out[mode] = clean
        return out

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
