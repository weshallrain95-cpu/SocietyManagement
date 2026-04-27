from rest_framework.decorators import api_view
from rest_framework.response import Response
from society.models import OperationalRule
from society.api.serializers.operational_rule import OperationalRuleSerializer


@api_view(["GET"])
def get_operational_rules(request):
    society_id = request.GET.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    try:
        rule = OperationalRule.objects.get(society_id=society_id)
    except OperationalRule.DoesNotExist:
        return Response({})

    serializer = OperationalRuleSerializer(rule)
    return Response(serializer.data)

@api_view(["POST"])
def save_operational_rules(request):
    society_id = request.data.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    rule, _ = OperationalRule.objects.get_or_create(society_id=society_id)

    serializer = OperationalRuleSerializer(rule, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"success": True})

    return Response(serializer.errors, status=400)
