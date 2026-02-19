from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from bylaws.models import BylawDecision


@api_view(["GET"])
def list_bylaw_decisions(request):
    """
    Returns all by-law decisions in sequence order.
    Used by By-law Decision Workspace UI.
    """
    decisions = BylawDecision.objects.filter(is_active=True).order_by("sequence_order")

    data = []
    for d in decisions:
        data.append({
            "id": d.id,
            "decision_code": d.decision_code,
            "question": d.question,
            "description": d.description,
            "default_value": d.default_value,
            "legal_reference": d.legal_reference,
            "allowed_values": d.allowed_values,
            "category": d.category,
            "sequence_order": d.sequence_order,
        })

    return Response({"decisions": data})

from society.models import Society
from statutory.models import SocietyBylawDecision


@api_view(["POST"])
def save_bylaw_decisions(request, society_id):
    """
    Saves decisions taken by a society.
    Payload:
    {
        decisions: [
            { decision_code: "...", value: "..." }
        ]
    }
    """

    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return Response({"error": "Society not found"}, status=status.HTTP_404_NOT_FOUND)

    decisions_payload = request.data.get("decisions", [])

    if not decisions_payload:
        return Response({"error": "No decisions provided"}, status=status.HTTP_400_BAD_REQUEST)

    for item in decisions_payload:
        decision_code = item.get("decision_code")
        value = item.get("value")

        try:
            decision = BylawDecision.objects.get(decision_code=decision_code)
        except BylawDecision.DoesNotExist:
            continue

        SocietyBylawDecision.objects.update_or_create(
            society=society,
            decision=decision,
            defaults={"value": value}
        )

    return Response({"success": True})

from rest_framework.response import Response
from rest_framework.decorators import api_view

from bylaws.models import (
    BylawVersion,
    BylawChapter,
    BylawClause,
    BylawSubClause
)
from rest_framework import serializers

class BylawSubClauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BylawSubClause
        fields = ["sub_clause_number", "legal_text", "sequence_order"]


class BylawClauseSerializer(serializers.ModelSerializer):
    sub_clauses = BylawSubClauseSerializer(many=True)

    class Meta:
        model = BylawClause
        fields = [
            "clause_number",
            "title",
            "legal_text",
            "sequence_order",
            "sub_clauses"
        ]


class BylawChapterSerializer(serializers.ModelSerializer):
    clauses = BylawClauseSerializer(many=True)

    class Meta:
        model = BylawChapter
        fields = [
            "chapter_number",
            "title",
            "sequence_order",
            "clauses"
        ]


class BylawVersionSerializer(serializers.ModelSerializer):
    chapters = BylawChapterSerializer(many=True)

    class Meta:
        model = BylawVersion
        fields = [
            "code",
            "title",
            "is_active",
            "chapters"
        ]
@api_view(["GET"])
def full_bylaw_version(request, code):
    version = BylawVersion.objects.prefetch_related(
        "chapters__clauses__sub_clauses"
    ).get(code=code)

    serializer = BylawVersionSerializer(version)
    return Response(serializer.data)

from django.shortcuts import render
from bylaws.models import BylawVersion


def bylaws_viewer(request):
    version = BylawVersion.objects.filter(is_active=True).first()

    if not version:
        return render(request, "bylaws/viewer.html", {"chapters": []})

    chapters = version.chapters.all().order_by("sequence_order")

    return render(request, "bylaws/viewer.html", {
        "chapters": chapters
    })

