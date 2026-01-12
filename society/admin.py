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
from society.services import approve_pending_transaction


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
            approve_pending_transaction(
                pending_txn=txn,
                approved_by=request.user,
            )

    approve_transactions.short_description = "Approve selected transactions"
