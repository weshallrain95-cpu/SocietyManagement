from django.contrib import admin
from statutory.models import (
    State,
    LegalStage,
    LegalObligation,
    LegalChecklistItem,
    LegalArtifactTemplate,
    SocietyLegalProgress,
    SocietyObligationStatus,
)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


@admin.register(LegalStage)
class LegalStageAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "sequence_order", "is_mandatory")
    list_filter = ("state",)
    ordering = ("state", "sequence_order")


@admin.register(LegalObligation)
class LegalObligationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_mandatory", "sequence_order")
    list_filter = ("legal_stage",)


@admin.register(LegalChecklistItem)
class LegalChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("description", "legal_obligation", "mandatory")


@admin.register(LegalArtifactTemplate)
class LegalArtifactTemplateAdmin(admin.ModelAdmin):
    list_display = ("artifact_type", "legal_obligation")


@admin.register(SocietyLegalProgress)
class SocietyLegalProgressAdmin(admin.ModelAdmin):
    list_display = ("society", "legal_stage", "status", "started_on")
    list_filter = ("status",)


@admin.register(SocietyObligationStatus)
class SocietyObligationStatusAdmin(admin.ModelAdmin):
    list_display = ("society", "legal_obligation", "status")
    list_filter = ("status",)
from statutory.models import StatutoryAuditLog

@admin.register(StatutoryAuditLog)
class StatutoryAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "society",
        "action",
        "legal_stage",
        "source",
        "created_at",
    )
    list_filter = ("action", "source", "society")
    readonly_fields = (
        "society",
        "legal_stage",
        "action",
        "description",
        "performed_by",
        "source",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
from django.contrib import admin
from .models import SocietyLegalDocument


@admin.register(SocietyLegalDocument)
class SocietyLegalDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "society",
        "template",
        "status",
        "uploaded_at",
    )

    list_filter = (
        "status",
        "template",
    )

    search_fields = (
        "society__name",
        "template__name",
    )
