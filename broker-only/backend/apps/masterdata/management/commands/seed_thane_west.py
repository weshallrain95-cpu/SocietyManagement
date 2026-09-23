"""Load the Thane West pilot master data, and optionally synthetic demo data for the laptop.

python manage.py seed_thane_west            # master data only (safe for staging)
python manage.py seed_thane_west --demo     # + demo brokers, staff, listings, customers (laptop only)
"""

import random
from datetime import timedelta
from pathlib import Path

import yaml
from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Point
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.masterdata import dedupe
from apps.masterdata.location import compute_for_building
from apps.masterdata.models import AttributeDef, Building, Locality, MicroMarket, Poi, Society, SocietyAlias
from common.crypto import phone_hash

SEED = Path(__file__).resolve().parents[2] / "seed" / "thane_west.yaml"


def pt(d):
    return Point(float(d["lng"]), float(d["lat"]), srid=4326)


class Command(BaseCommand):
    help = "Seed Thane West pilot master data (and --demo data for local development)."

    def add_arguments(self, parser):
        parser.add_argument("--demo", action="store_true", help="Also create synthetic brokers, listings and customers")
        parser.add_argument("--dictionary", help="Path to the attribute dictionary (.yaml or review .xlsx)")

    def handle(self, demo, dictionary, **_):
        data = yaml.safe_load(SEED.read_text(encoding="utf-8"))
        with transaction.atomic():
            mm, _ = MicroMarket.objects.update_or_create(
                name=data["micro_market"]["name"], defaults={"launch_state": data["micro_market"]["launch_state"]}
            )
            locs = {}
            for loc in data["localities"]:
                locs[loc["name"]], _ = Locality.objects.update_or_create(
                    micro_market=mm, name=loc["name"], defaults={"centroid": pt(loc), "pincodes": loc["pincodes"]}
                )
            for p in data["pois"]:
                Poi.objects.update_or_create(type=p["type"], name=p["name"], defaults={"location": pt(p), "source": "seed_approx"})
            for s in data["societies"]:
                soc, _ = Society.objects.update_or_create(
                    canonical_name=s["name"],
                    locality=locs[s["locality"]],
                    defaults={
                        "location": pt(s),
                        "kind": s.get("kind", "chs"),
                        "provenance": {"source": "seed_thane_west", "verified": False},
                    },
                )
                for a in s.get("aliases", []):
                    dedupe.learn_alias(soc, a, SocietyAlias.Source.SEED)
        self.stdout.write(
            self.style.SUCCESS(f"Thane West: {len(locs)} localities, {len(data['societies'])} societies, {len(data['pois'])} POIs")
        )
        if not AttributeDef.objects.exists():
            self._load_dictionary(dictionary)
        if demo:
            if not settings.DEBUG:
                raise CommandError("--demo is for the laptop only (DJANGO_DEBUG=true)")
            self._demo(mm, locs)

    def _load_dictionary(self, path):
        from apps.masterdata import dictionary

        candidates = [path] if path else [str(dictionary.DEFAULT_PATH)]
        fallback = Path(settings.BASE_DIR) / "tests" / "fixtures" / "attributes_min.yaml"
        for c in candidates:
            if c and Path(c).exists():
                args = [c] + (["--all-rows"] if c.endswith(".xlsx") else [])
                call_command("load_attribute_dictionary", *args)
                return
        self.stdout.write(
            self.style.WARNING(
                "Approved attribute dictionary not found yet (pending founder approval). "
                "Loading the minimal test set so the app works; pass --dictionary <review.xlsx> to load the full draft."
            )
        )
        call_command("load_attribute_dictionary", str(fallback))

    def _demo(self, mm, locs):
        from apps.crm import services as crm
        from apps.identity.models import User
        from apps.inventory.services import create_listing, set_keys
        from apps.masterdata.services import get_or_create_building, get_or_create_unit
        from apps.orgs.models import BrokerOrg, Membership, ServiceArea
        from apps.orgs.serializers import circle
        from common import rls

        rng = random.Random(42)  # deterministic demo data
        admin_phone = "9000000000"
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(admin_phone, password="onlybroker-dev-admin", display_name="Platform Admin")
        brokers = [
            ("Demo Realty Dhokali", "9820000001", "Dhokali", ["RENT", "SALE_RESALE"]),
            ("Demo Estates Manpada", "9820000002", "Manpada", ["RENT"]),
            ("Demo Homes Hiranandani", "9820000003", "Hiranandani Estate", ["RENT", "SALE_RESALE", "SALE_NEW"]),
        ]
        societies = list(Society.objects.filter(locality__micro_market=mm, status="active"))
        furn = ["unfurnished", "semi-furnished", "fully furnished"]
        pets = ["no", "cats only", "small dogs", "all pets", "case-by-case"]
        n_listings = 0
        for i, (name, phone, loc, txns) in enumerate(brokers):
            user = User.objects.filter(phone_hash=phone_hash("+91" + phone)).first() or User.objects.create_user(
                phone, display_name=f"{name} (principal)"
            )
            org, created = BrokerOrg.objects.get_or_create(
                name=name,
                defaults={
                    "txn_types": txns,
                    "verification_status": "verified",
                    "office_location": locs[loc].centroid,
                    "rera_agent_no": f"A5170000000{i}",
                },
            )
            if not created:
                continue
            Membership.objects.get_or_create(user=user, org=org, active=True, defaults={"role": "broker_principal"})
            staff = User.objects.create_user(f"98200100{i}0", display_name=f"Field staff {i + 1}")
            Membership.objects.create(user=staff, org=org, role="broker_staff")
            ServiceArea.objects.create(
                org=org, label=f"{loc} 4 km", txn_types=txns, area=MultiPolygon(circle(locs[loc].centroid, 4), srid=4326)
            )
            with rls.org_context(org.pk):
                for _ in range(20):
                    soc = rng.choice(societies)
                    b = get_or_create_building(soc, rng.choice(["A", "B", "C"]))
                    floor = rng.randint(1, 20)
                    bhk = rng.choice([1, 1, 2, 2, 2, 3])
                    unit, _ = get_or_create_unit(b, f"{floor}{rng.randint(1, 8):02d}", bhk=bhk, floor=floor)
                    rent = int(round((12000 + bhk * 9000 + rng.randint(-3000, 6000)) / 500) * 500)
                    txn = "RENT" if "RENT" in txns and rng.random() < 0.8 else txns[-1]
                    data = {"asking_rent": rent, "deposit": rent * 3} if txn == "RENT" else {"asking_price": rent * 420}
                    data["available_from"] = timezone.localdate() + timedelta(days=rng.randint(0, 45))
                    listing, created = create_listing(
                        org=org,
                        user=user,
                        unit=unit,
                        txn_type=txn,
                        data=data,
                        owner_phone=f"98190{rng.randint(10000, 99999)}",
                        attributes={
                            "furnishing": rng.choice(furn),
                            "pets_allowed": rng.choice(pets),
                            "car_parking_covered": rng.choice([0, 1, 1, 2]),
                            "lift": True,
                            "nonveg_cooking": rng.choice(["allowed", "allowed", "not allowed"]),
                        },
                    )
                    if created:
                        set_keys(listing, holder_type=rng.choice(["office", "owner", "society_office"]))
                        n_listings += 1
                for j in range(3):
                    c, _ = crm.capture_customer(
                        org=org,
                        user=user,
                        phone=f"98765{i}{j}0000"[:10],
                        name=f"Demo customer {i}{j}",
                        source=rng.choice(["walk_in", "phone_call", "referral"]),
                    )
                    crm.add_requirement(
                        c,
                        {
                            "txn_type": "RENT",
                            "bhk_min": 2,
                            "bhk_max": 2,
                            "budget_max": 30000,
                            "house_rule_needs": {"pets": "dog"} if j == 0 else {},
                        },
                    )
        for b in Building.objects.all():
            compute_for_building(b)
        from apps.marketplace.tasks import rebuild_supply

        rebuild_supply(force=True)
        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data: {len(brokers)} brokers, {n_listings} listings.\n"
                f"  Broker logins (OTP shown in API response in dev): 9820000001 / 9820000002 / 9820000003\n"
                f"  Django admin: http://localhost:8000/django-admin/  phone {admin_phone} / password onlybroker-dev-admin"
            )
        )
