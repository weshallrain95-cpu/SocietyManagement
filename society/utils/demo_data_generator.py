import random
from datetime import date

from django.db import transaction

from society.models import (
    Society,
    Flat,
    Person,
    SocietyMember,
    MaintenanceBill,
    Payment,
)


FIRST_NAMES = [
    "Raj", "Amit", "Sanjay", "Vikas", "Neha",
    "Pooja", "Anita", "Rahul", "Kiran", "Arjun"
]

LAST_NAMES = [
    "Sharma", "Patel", "Rane", "Mehta", "Gupta",
    "Desai", "Kulkarni", "Shah", "Nair", "Joshi"
]


class SocietyDemoDataGenerator:

    def populate_society(self, society):

        # ✔ Guard goes HERE (inside function)

        if SocietyMember.objects.filter(society=society).count() > 10:
            raise Exception("Demo data already generated for this society.")

        flats = Flat.objects.filter(society=society)

        if not flats.exists():
            raise Exception("Society has no flats. Run Formation Accelerator first.")

        created_people = 0
        created_members = 0
        bills_created = 0
        payments_created = 0

        with transaction.atomic():

            for flat in flats:

                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)

                person = Person.objects.create(
                    full_name=f"{first} {last}",
                    phone=f"98{random.randint(10000000,99999999)}",
                    email=f"{first.lower()}.{last.lower()}{random.randint(1,999)}@demo.com",
                    is_verified=True
                )

                created_people += 1

                from datetime import date

                SocietyMember.objects.create(
                    society=society,
                    person=person,
                    admitted_on=date.today(),
                    is_active=True
                )

                created_members += 1

                amount = random.randint(2500, 6000)

                MaintenanceBill.objects.create(
                    society=society,
                    flat=flat,
                    amount=amount,
                    bill_date=date.today()
                )

                bills_created += 1

                if random.random() < 0.8:

                    Payment.objects.create(
                        society=society,
                        flat=flat,
                        amount=amount,
                        payment_date=date.today()
                    )

                    payments_created += 1

        return {
            "people_created": created_people,
            "members_created": created_members,
            "bills_created": bills_created,
            "payments_created": payments_created
        }