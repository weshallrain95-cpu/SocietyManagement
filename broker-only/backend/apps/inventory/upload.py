"""Bulk inventory upload (INV-03, PRD J4): parse -> map columns -> resolve -> review -> commit."""

import csv
import hashlib
import io
import re
from datetime import date, datetime

from django.db import transaction
from django.utils import timezone

from apps.masterdata import dedupe
from apps.masterdata.models import Locality, Society, SocietyAlias
from apps.masterdata.normalise import normalise_name, normalise_unit_no
from apps.masterdata.services import get_or_create_building, get_or_create_unit, propose_society

from .models import SavedColumnMapping, UploadBatch, UploadRow
from .services import create_listing

# Target field -> header spellings seen in broker sheets (lower-case, punctuation stripped).
SYNONYMS = {
    "society": [
        "society",
        "building",
        "bldg",
        "society name",
        "building name",
        "bldg name",
        "soc name",
        "project name",
        "project",
        "complex",
        "soc",
        "property",
        "name",
    ],
    "wing": ["wing", "tower", "block", "bldg no", "building no"],
    "unit_no": ["flat", "flat no", "unit", "unit no", "flat number", "room no", "apt no"],
    "floor": ["floor", "flr"],
    "bhk": ["bhk", "config", "configuration", "type", "bedrooms", "rooms"],
    "property_type": ["property type", "prop type"],
    "txn_type": ["rent sale", "transaction", "for", "purpose", "listing type"],
    "asking_rent": ["rent", "rent amount", "expected rent", "monthly rent", "rental"],
    "asking_price": ["price", "sale price", "expected price", "cost", "quote"],
    "deposit": ["deposit", "dep", "security deposit", "sd"],
    "maintenance": ["maintenance", "maint", "society charges"],
    "available_from": ["available from", "availability", "avail", "available date", "vacant from"],
    "owner_name": ["owner", "owner name", "landlord"],
    "owner_phone": ["owner phone", "owner mobile", "owner contact", "owner no", "contact", "mobile"],
    "locality": ["locality", "area", "location", "sector"],
    "pincode": ["pincode", "pin", "pin code", "zip"],
    "lat": ["lat", "latitude"],
    "lng": ["lng", "lon", "long", "longitude"],
    "carpet_sqft": ["carpet", "carpet area", "area sqft", "sqft", "sq ft", "size"],
    "furnishing": ["furnishing", "furn", "furnished"],
    "pets_allowed": ["pets", "pet", "pets allowed", "pet friendly"],
    "car_parking_covered": ["parking", "car parking", "covered parking"],
    "nonveg_cooking": ["non veg", "nonveg", "non veg allowed"],
    "bachelors_allowed": ["bachelors", "bachelor", "bachelors allowed"],
    "private_notes": ["notes", "remarks", "comment", "comments"],
}
ATTRIBUTE_TARGETS = {"furnishing", "pets_allowed", "car_parking_covered", "nonveg_cooking", "bachelors_allowed"}


def _norm_header(h) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(h or "").lower()).strip()


def guess_mapping(headers: list[str]) -> dict:
    mapping = {}
    used = set()
    for target, names in SYNONYMS.items():
        for h in headers:
            if h in used:
                continue
            if _norm_header(h) in names:
                mapping[h] = target
                used.add(h)
                break
    return mapping


def header_signature(headers) -> str:
    return hashlib.sha256("|".join(_norm_header(h) for h in headers).encode()).hexdigest()


def read_table(filename: str, content: bytes) -> tuple[list[str], list[dict]]:
    if filename.lower().endswith((".xlsx", ".xlsm")):
        from openpyxl import load_workbook

        ws = load_workbook(io.BytesIO(content), read_only=True, data_only=True).worksheets[0]
        it = ws.iter_rows(values_only=True)
        headers = [str(h).strip() if h is not None else "" for h in next(it)]
        rows = [dict(zip(headers, r, strict=False)) for r in it if any(v not in (None, "") for v in r)]
    else:
        text = content.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        headers = [h.strip() for h in reader.fieldnames or []]
        rows = [{k.strip(): v for k, v in r.items() if k} for r in reader if any((v or "").strip() for v in r.values())]
    return [h for h in headers if h], rows


def _clean(v):
    if isinstance(v, str):
        v = v.strip()
        # Excel formula injection: never keep a leading = + - @ as formula text.
        if v[:1] in ("=", "+", "@"):
            v = "'" + v
    return v


def _money(v):
    if v in (None, ""):
        return None
    s = str(v).lower().replace(",", "").replace("₹", "").replace("rs", "").strip()
    mult = 1
    for suffix, m in (("cr", 10_000_000), ("crore", 10_000_000), ("l", 100_000), ("lac", 100_000), ("lakh", 100_000), ("k", 1000)):
        if s.endswith(suffix):
            s, mult = s[: -len(suffix)].strip(), m
            break
    return int(round(float(s) * mult))


def _bhk(v):
    s = str(v or "").lower().replace(" ", "")
    if "rk" in s:
        return 0.5
    m = re.search(r"(\d+(?:\.5)?)", s)
    if not m:
        raise ValueError(f"BHK not understood: {v!r}")
    return float(m.group(1))


def _date(v):
    if v in (None, ""):
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip().lower()
    if s in ("now", "immediate", "immediately", "ready", "vacant"):
        return timezone.localdate()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%d %b %Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(s.title() if "%b" in fmt else s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date not understood: {v!r}")


def _txn(v, default):
    s = str(v or "").lower()
    if not s:
        return default
    if "rent" in s or "lease" in s or "l&l" in s:
        return "RENT"
    if "new" in s or "builder" in s or "under construction" in s:
        return "SALE_NEW"
    if "sale" in s or "resale" in s or "buy" in s:
        return "SALE_RESALE"
    return default


def parse_row(raw: dict, mapping: dict, default_txn: str) -> tuple[dict, list[str]]:
    get = {target: _clean(raw.get(header)) for header, target in mapping.items()}
    parsed, errors = {"attributes": {}}, []
    if not get.get("society"):
        errors.append("Society / building name is missing")
    else:
        parsed["society"] = str(get["society"])
    if not get.get("unit_no"):
        errors.append("Flat number is missing")
    else:
        u = normalise_unit_no(str(get["unit_no"]))
        parsed["unit_no"] = str(get["unit_no"])
        parsed["wing"] = str(get.get("wing") or u.wing or normalise_name(parsed.get("society", "")).building_hint or "")
        parsed["floor"] = int(get["floor"]) if str(get.get("floor") or "").strip().lstrip("-").isdigit() else u.floor
    parsed["txn_type"] = _txn(get.get("txn_type"), default_txn)
    for field, fn in (
        ("bhk", _bhk),
        ("asking_rent", _money),
        ("asking_price", _money),
        ("deposit", _money),
        ("maintenance", _money),
        ("available_from", _date),
        ("carpet_sqft", _money),
    ):
        if get.get(field) not in (None, ""):
            try:
                parsed[field] = fn(get[field])
            except (ValueError, TypeError) as e:
                errors.append(str(e) if isinstance(e, ValueError) and str(e) else f"{field}: {get[field]!r} not understood")
    if "bhk" not in parsed and "bhk" not in [e.split(":")[0] for e in errors]:
        errors.append("BHK is missing")
    if parsed["txn_type"] == "RENT" and not parsed.get("asking_rent") and parsed.get("asking_price"):
        parsed["asking_rent"] = parsed.pop("asking_price")
    for k in ("owner_name", "owner_phone", "locality", "pincode", "private_notes", "property_type"):
        if get.get(k) not in (None, ""):
            parsed[k] = str(get[k])
    for k in ("lat", "lng"):
        if get.get(k) not in (None, ""):
            try:
                parsed[k] = float(get[k])
            except ValueError:
                errors.append(f"{k} is not a number")
    for k in ATTRIBUTE_TARGETS:
        if get.get(k) not in (None, ""):
            parsed["attributes"][k] = str(get[k])
    return parsed, errors


def create_batch(
    *, org, user, filename: str, content: bytes, micro_market=None, default_txn_type="RENT", mapping: dict | None = None
) -> UploadBatch:
    headers, rows = read_table(filename, content)
    sig = header_signature(headers)
    if mapping is None:
        saved = SavedColumnMapping.objects.filter(org=org, header_signature=sig).first()
        mapping = saved.mapping if saved else guess_mapping(headers)
    else:
        SavedColumnMapping.objects.update_or_create(org=org, header_signature=sig, defaults={"mapping": mapping})
    batch = UploadBatch.objects.create(
        org=org,
        uploaded_by=user,
        filename=filename[:200],
        micro_market=micro_market,
        default_txn_type=default_txn_type,
        column_mapping=mapping,
    )
    resolve_batch(batch, rows)
    return batch


def resolve_batch(batch: UploadBatch, rows: list[dict]) -> None:
    localities = {}
    if batch.micro_market_id:
        localities = {loc.name_normalised: loc for loc in Locality.objects.filter(micro_market_id=batch.micro_market_id)}
    to_create = []
    for i, raw in enumerate(rows, start=2):  # row 1 is the header in the broker's sheet
        raw_json = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in raw.items()}
        parsed, errors = parse_row(raw, batch.column_mapping, batch.default_txn_type)
        row = UploadRow(
            org=batch.org,
            batch=batch,
            row_no=i,
            raw=raw_json,
            errors=errors,
            parsed={k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in parsed.items()},
        )
        if errors:
            row.resolution = UploadRow.Resolution.ERROR
        else:
            locality = localities.get(normalise_name(parsed.get("locality", "")).text) if parsed.get("locality") else None
            point = None
            if "lat" in parsed and "lng" in parsed:
                from django.contrib.gis.geos import Point

                point = Point(parsed["lng"], parsed["lat"], srid=4326)
            cands = dedupe.find_candidates(
                parsed["society"],
                point=point,
                pincode=parsed.get("pincode", ""),
                locality=locality,
                micro_market=batch.micro_market,
                include_provisional_for_org=batch.org,
            )
            decision = dedupe.decide(cands)
            row.candidates = [c.as_dict() for c in cands[:3]]
            if decision.action == "auto":
                row.society = decision.best.society
                row.resolution = UploadRow.Resolution.AUTO
            elif decision.action == "confirm":
                row.resolution = UploadRow.Resolution.NEEDS_CONFIRMATION
            else:
                row.resolution = UploadRow.Resolution.PROVISIONAL
        to_create.append(row)
    UploadRow.objects.bulk_create(to_create, batch_size=500)
    _recount(batch)
    batch.state = UploadBatch.State.AWAITING_REVIEW
    batch.save(update_fields=["state", "counts"])


def _recount(batch):
    from django.db.models import Count

    batch.counts = {r["resolution"]: r["n"] for r in batch.rows.values("resolution").annotate(n=Count("id"))}
    batch.counts["total"] = sum(v for k, v in batch.counts.items() if k != "total")


@transaction.atomic
def resolve_row(row: UploadRow, *, user, society_id=None, propose: dict | None = None, skip=False) -> UploadRow:
    """Broker's decision on a row that could not be matched automatically."""
    if row.resolution in (UploadRow.Resolution.COMMITTED, UploadRow.Resolution.ERROR):
        raise ValueError("This row cannot be changed")
    if skip:
        row.resolution = UploadRow.Resolution.SKIPPED
    elif society_id:
        society = Society.objects.get(pk=society_id, status__in=[Society.Status.ACTIVE, Society.Status.PROVISIONAL])
        if society.status == Society.Status.PROVISIONAL and society.proposed_by_org_id != row.org_id:
            raise ValueError("That society is not available yet")
        row.society = society
        row.resolution = UploadRow.Resolution.BROKER_CONFIRMED
        dedupe.learn_alias(society, row.parsed["society"], SocietyAlias.Source.BROKER_CONFIRMED, org=row.org)
    elif propose:
        from django.contrib.gis.geos import Point

        locality = Locality.objects.get(pk=propose["locality_id"])
        point = Point(float(propose["lng"]), float(propose["lat"]), srid=4326)
        row.society = propose_society(
            name=propose.get("name") or row.parsed["society"],
            locality=locality,
            location=point,
            org=row.org,
            address=propose.get("address", ""),
            pincode=propose.get("pincode", ""),
            user=user,
            candidates=row.candidates,
        )
        row.resolution = UploadRow.Resolution.PROVISIONAL
    else:
        raise ValueError("Choose a society, propose a new one, or skip the row")
    row.save()
    _recount(row.batch)
    row.batch.save(update_fields=["counts"])
    return row


def commit_batch(batch: UploadBatch, *, user) -> dict:
    """Create listings for every resolved row. Unresolved rows stay for later."""
    done = 0
    for row in batch.rows.filter(society__isnull=False).exclude(
        resolution__in=[UploadRow.Resolution.COMMITTED, UploadRow.Resolution.SKIPPED, UploadRow.Resolution.ERROR]
    ):
        with transaction.atomic():
            p = row.parsed
            building = get_or_create_building(row.society, p.get("wing") or None)
            unit, _ = get_or_create_unit(
                building, p["unit_no"], bhk=p["bhk"], floor=p.get("floor"), property_type=p.get("property_type") or "apartment"
            )
            data = {
                k: p.get(k)
                for k in (
                    "asking_rent",
                    "asking_price",
                    "deposit",
                    "maintenance",
                    "owner_name",
                    "private_notes",
                    "bhk",
                    "carpet_sqft",
                    "floor",
                )
            }
            if p.get("available_from"):
                data["available_from"] = date.fromisoformat(p["available_from"])
            from apps.masterdata.models import AttributeDef
            from apps.masterdata.resolver import InvalidValue, validate_value

            attributes, warnings = {}, []
            defs = {a.key: a for a in AttributeDef.objects.filter(key__in=list(p.get("attributes", {})), active=True)}
            for k, v in p.get("attributes", {}).items():
                try:
                    if k in defs:
                        validate_value(defs[k], v)
                    attributes[k] = v
                except InvalidValue as e:
                    warnings.append(f"Ignored {e}")  # a bad optional value never blocks the flat
            try:
                listing, _ = create_listing(
                    org=batch.org,
                    user=user,
                    unit=unit,
                    txn_type=p["txn_type"],
                    data=data,
                    attributes=attributes,
                    owner_phone=_safe_phone(p.get("owner_phone")),
                    origin="upload",
                    source_type="upload",
                )
            except InvalidValue as e:
                row.errors = [str(e)]
                row.resolution = UploadRow.Resolution.ERROR
                row.save(update_fields=["errors", "resolution"])
                continue
            if row.resolution == UploadRow.Resolution.AUTO:
                dedupe.learn_alias(row.society, p["society"], SocietyAlias.Source.BROKER_UPLOAD, org=batch.org)
            row.listing = listing
            row.resolution = UploadRow.Resolution.COMMITTED
            row.errors = warnings
            row.save(update_fields=["listing", "resolution", "errors"])
            done += 1
    _recount(batch)
    if not batch.rows.filter(resolution__in=[UploadRow.Resolution.NEEDS_CONFIRMATION]).exists():
        batch.state = UploadBatch.State.COMMITTED
    batch.save(update_fields=["state", "counts"])
    return {"committed": done, **batch.counts}


def _safe_phone(v):
    from common.crypto import normalise_phone

    try:
        return normalise_phone(v) if v else None
    except ValueError:
        return None
