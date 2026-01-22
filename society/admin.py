from django.contrib import admin

from society.models import (
    Society,
    ChartOfAccount,
    TransactionRule,
)

# -----------------------------
# Society
# -----------------------------
@admin.register(Society)
class SocietyAdmin(admin.ModelAdmin):
    list_display = ("name", "registration_number")
    search_fields = ("name", "registration_number")


# -----------------------------
# Chart of Accounts
# -----------------------------
@admin.register(ChartOfAccount)
class ChartOfAccountAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "account_type",
        "is_system",
        "society",
    )

    list_filter = (
        "account_type",
        "is_system",
        "society",
    )

    search_fields = (
        "code",
        "name",
    )

    ordering = ("code",)


# -----------------------------
# Transaction Rules
# -----------------------------
@admin.register(TransactionRule)
class TransactionRuleAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_type",
        "debit_account_code",
        "credit_account_code",
        "society",
        "is_active",
    )

    list_filter = (
        "transaction_type",
        "society",
        "is_active",
    )

    search_fields = (
        "transaction_type",
        "debit_account_code",
        "credit_account_code",
    )

    ordering = ("society", "transaction_type")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("transaction_type", "society")
        return ()

from django.contrib import admin
from society.models import PendingTransaction
from society import services as legacy_services


@admin.register(PendingTransaction)
class PendingTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "transaction_type",
        "amount",
        "status",
        "society",
        "created_by",
        "approved_by",
        "created_at",
    )

    list_filter = ("status", "transaction_type", "society")

    actions = ["approve_transactions"]

    def approve_transactions(self, request, queryset):
        for txn in queryset:
            legacy_services.approve_pending_transaction(
                pending_txn=txn,
                approved_by=request.user,
            )

    approve_transactions.short_description = "Approve selected transactions"

from django.contrib import admin
from society.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "event_type",
        "domain",
        "object_type",
        "object_id",
        "actor_id",
        "short_hash",
    )

    list_filter = (
        "domain",
        "event_type",
        "object_type",
    )

    search_fields = (
        "object_id",
        "actor_id",
        "event_hash",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "event_type",
        "domain",
        "object_type",
        "object_id",
        "actor_id",
        "payload_pretty",
        "event_hash",
    )

    def short_hash(self, obj):
        return obj.event_hash[:12]

    short_hash.short_description = "Hash"
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    def payload_pretty(self, obj):
        import json
        return json.dumps(obj.payload, indent=2)

    payload_pretty.short_description = "Payload"
