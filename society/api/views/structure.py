from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import Society
from society.services import generate_society_structure
from society.services_group_engine import generate_grouped_structure


# =============================
# 🔥 EXPANSION + INDEX ENGINE
# =============================
def expand_flat_structure(flat_structure):
    """
    EXPANDS + ASSIGNS INDEX

    Output format:
    [
        {"type": "1BHK", "area": 350, "index": 1},
        ...
    ]
    """

    expanded = []
    index_counter = 1

    for config in flat_structure:
        flat_type = config.get("type")
        area = config.get("area")
        count = config.get("count", 1)

        for _ in range(count):
            expanded.append({
                "type": flat_type,
                "area": area,
                "index": index_counter,
            })
            index_counter += 1

    return expanded


# =============================
# 🚀 MAIN API
# =============================
@api_view(["POST"])
def generate_structure(request):
    print("🔥 ACTUAL REQUEST DATA:", request.data)
    data = request.data
    
    
    society_id = data.get("society_id")
    structure_type = data.get("structure_type")

    society = get_object_or_404(Society, id=society_id)

    try:

        # =========================================
        # ✅ STANDARD FLOW (SINGLE / MULTI uniform)
        # =========================================
        if structure_type == "SINGLE":

            total_wings = data.get("total_wings") or 1
            floors_per_wing = data.get("floors_per_wing") or data.get("floors")
            flat_structure = data.get("flat_structure", [])
            numbering_style = data.get("flat_numbering_style", "A-101")

            # 🔥 CORRECTED — EXPAND + INDEX
            expanded_layout = expand_flat_structure(flat_structure)

            # 🔥 REMOVE index before sending to engine
            floor_layout = [
                {
                    "type": item["type"],
                    "area": item["area"]
                }
                for item in expanded_layout
            ]

            result = generate_society_structure(
                society=society,
                total_wings=total_wings,
                floors_per_wing=floors_per_wing,
                floor_layout=floor_layout,
                flat_numbering_style=numbering_style,
            )

            # =============================
            # ✅ NEW: UPDATE ONBOARDING STAGE
            # =============================
            society.onboarding_stage = "STRUCTURE_CREATED"
            society.save(update_fields=["onboarding_stage"])

            return Response({
                "status": "success",
                "engine": "standard",
                "data": result,
            })

        
        # =========================================
        # ✅ GROUP FLOW (FIXED — SINGLE + GROUP SAFE)
        # =========================================

        elif structure_type == "GROUP":

            total_wings = data.get("total_wings") or 1
            floors_per_wing = data.get("floors_per_wing") or data.get("floors")

            print("DEBUG RAW DATA:", data)
            print("DEBUG GROUPS:", data.get("groups"))

            # 🔥 FINAL FIX — derive from groups if still None
            if not floors_per_wing:
                groups = data.get("groups", [])
                all_floors = set()

                for g in groups:
                    all_floors.update(g.get("floors", []))

                if not all_floors:
                    return Response({"error": "No floors defined in groups"}, status=400)

                floors_per_wing = max(all_floors)

            
            result = generate_grouped_structure(
                society=society,
                total_wings=total_wings,
                floors_per_wing=floors_per_wing,
                groups=data.get("groups"),
                flat_numbering_style=data.get("flat_numbering_style", "A-101"),
            )

            # =============================
            # ✅ NEW: UPDATE ONBOARDING STAGE
            # =============================
            society.onboarding_stage = "STRUCTURE_CREATED"
            society.save(update_fields=["onboarding_stage"])

            return Response({
                "status": "success",
                "engine": "group",
                "data": result,
            })


        else:
            return Response({
                "error": "Invalid structure_type"
            }, status=400)

    except Exception as e:
        return Response({
            "status": "failed",
            "error": str(e)
        }, status=500)