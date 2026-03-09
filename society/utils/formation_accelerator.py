from society.models import Society, Wing, Floor, Flat
from django.db import transaction


class SocietyFormationAccelerator:
    """
    Generates the structural layout of a society.

    Creates:
    - Wings
    - Floors
    - Flats

    Designed for rapid onboarding of a newly registered society.
    """

    def generate_structure(
        self,
        society,
        wings,
        floors_per_wing,
        flats_per_floor,
        flat_numbering="floor_based",
    ):
        """
        Build full structural layout.

        Example:

        Wing A
          Floor 1 → Flats 101,102,103,104
          Floor 2 → Flats 201,202,203,204
        """

        created_wings = 0
        created_floors = 0
        created_flats = 0

        with transaction.atomic():

            for wing_name in wings:

                wing = Wing.objects.create(
                    society=society,
                    name=wing_name
                )

                created_wings += 1

                for floor_number in range(1, floors_per_wing + 1):

                    floor = Floor.objects.create(
                        wing=wing,
                        number=floor_number
                    )

                    created_floors += 1

                    for flat_index in range(1, flats_per_floor + 1):

                        flat_number = f"{wing_name}{floor_number}{flat_index:02d}"

                        Flat.objects.create(
                            society=society,
                            wing=wing.name,
                            wing_ref=wing,
                            floor=floor_number,
                            floor_ref=floor,
                            flat_number=flat_number,
                            is_active=True
                        )

                        created_flats += 1

        return {
            "wings_created": created_wings,
            "floors_created": created_floors,
            "flats_created": created_flats,
        }
