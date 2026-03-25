# ==========================================================
# GROUP STRUCTURE ENGINE (ADVANCED)
# ==========================================================

from django.db import transaction
from society.models import Wing, Floor, Flat
from society.services import generate_flat_number

WING_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def generate_wing_name(index: int) -> str:
    if index < len(WING_ALPHABET):
        return WING_ALPHABET[index]
    return f"W{index + 1}"


@transaction.atomic
def generate_grouped_structure(
    *,
    society,
    total_wings,
    floors_per_wing,
    groups,  # [{ floors: [], layout: [] }]
    flat_numbering_style="A-101",
):
    """
    Advanced structure generator supporting:

    - Floor grouping
    - Mixed flat configurations
    - Multiple wings

    groups format:
    [
        {
            "floors": [1,2,3],
            "layout": [
                {"type": "2BHK", "area": 800, "count": 2},
                {"type": "3BHK", "area": 1200, "count": 1}
            ]
        }
    ]
    """

    # -----------------------------------
    # SAFETY CHECK — prevent duplication
    # -----------------------------------
    if society.flats.exists():
        return {
            "status": "SKIPPED",
            "message": "Society structure already exists",
            "flats": society.flats.count(),
        }

    created_wings = 0
    created_floors = 0
    created_flats = 0

    # -----------------------------------
    # VALIDATION — floor coverage
    # -----------------------------------
    all_grouped_floors = set()

    for g in groups:
        for f in g["floors"]:
            if f in all_grouped_floors:
                raise ValueError(f"Floor {f} assigned multiple times")
            all_grouped_floors.add(f)

    expected_floors = set(range(1, floors_per_wing + 1))

    if all_grouped_floors != expected_floors:
        raise ValueError("All floors must be assigned to exactly one group")

    # -----------------------------------
    # MAIN LOOP
    # -----------------------------------
    for wing_index in range(total_wings):

        wing_name = generate_wing_name(wing_index)

        wing = Wing.objects.create(
            society=society,
            name=wing_name,
        )

        created_wings += 1

        # -----------------------------------
        # PROCESS GROUPS
        # -----------------------------------
        for group in groups:

            floors = group["floors"]
            layout = group["layout"]

            for floor_number in floors:

                floor = Floor.objects.create(
                    wing=wing,
                    number=floor_number,
                )

                created_floors += 1

                flat_index_counter = 1

                # -----------------------------------
                # PROCESS LAYOUT
                # -----------------------------------
                for config in layout:

                    flat_type = config.get("type")
                    area = config.get("area")
                    count = config.get("count", 1)

                    for _ in range(count):

                        flat_number = generate_flat_number(
                            wing_name,
                            floor_number,
                            flat_index_counter,
                            flat_numbering_style,
                        )

                        Flat.objects.create(
                            society=society,

                            # legacy fields
                            wing=wing_name,
                            floor=floor_number,

                            # canonical refs
                            wing_ref=wing,
                            floor_ref=floor,

                            flat_number=flat_number,
                            flat_type=flat_type,
                            carpet_area_sqft=area,
                        )

                        created_flats += 1
                        flat_index_counter += 1

    return {
        "status": "CREATED",
        "wings": created_wings,
        "floors": created_floors,
        "flats": created_flats,
    }
    