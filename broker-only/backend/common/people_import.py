"""Read a list of people (customers or fellow brokers) from Excel, CSV, a phone's contacts export (.vcf)
or pasted lines ("Name, 98200 12345, ..."). Returns plain rows; callers decide what to keep.
"""

import re

from .crypto import normalise_phone

MAX_ROWS = 5000


def _vcards(text: str) -> list[dict]:
    rows, cur = [], None
    for line in text.replace("\r\n ", "").splitlines():
        key, _, val = line.partition(":")
        k = key.split(";")[0].strip().upper()
        if k == "BEGIN":
            cur = {}
        elif k == "END" and cur is not None:
            rows.append(cur)
            cur = None
        elif cur is not None:
            if k == "FN":
                cur["name"] = val.strip()
            elif k == "TEL" and "phone" not in cur:
                cur["phone"] = val.strip()
            elif k == "ORG":
                cur["firm"] = val.replace(";", " ").strip()
            elif k == "ADR":
                cur["address"] = ", ".join(p.strip() for p in val.split(";") if p.strip())
            elif k == "NOTE":
                cur["notes"] = val.strip()
    return rows


def _pasted(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.search(r"(\+?\d[\d\s-]{8,}\d)", line)
        if not m:
            rows.append({"raw": line})
            continue
        rest = (line[: m.start()] + " " + line[m.end() :]).replace(",", " ").split()
        rows.append({"name": " ".join(rest)[:120], "phone": m.group(1)})
    return rows


def read_people(filename: str, content: bytes, columns: dict[str, tuple[str, ...]]) -> list[dict]:
    """`columns` maps our field to accepted header names (lower-case)."""
    name = (filename or "").lower()
    if name.endswith(".vcf"):
        rows = _vcards(content.decode("utf-8-sig", errors="replace"))
    elif name.endswith((".xlsx", ".xlsm", ".csv")):
        from apps.inventory.upload import read_table

        headers, raw = read_table(filename, content)
        lookup = {h: key for key, names in columns.items() for h in headers if str(h).strip().lower() in names}
        rows = [{lookup[h]: v for h, v in r.items() if h in lookup} for r in raw]
    else:
        rows = _pasted(content.decode("utf-8-sig", errors="replace"))
    if len(rows) > MAX_ROWS:
        raise ValueError(f"At most {MAX_ROWS} people per file")
    return rows


def clean_phone(v) -> str | None:
    if v in (None, ""):
        return None
    s = str(v).strip()
    if re.fullmatch(r"\d+\.0", s):  # Excel turns numbers into floats
        s = s[:-2]
    try:
        e164 = normalise_phone(s)
    except ValueError:
        return None
    digits = re.sub(r"\D", "", e164)
    return e164 if 11 <= len(digits) <= 13 else None


def text(v, limit: int) -> str:
    s = "" if v is None else str(v).strip()
    if s[:1] in ("=", "+", "@") and not re.fullmatch(r"\+?\d[\d\s-]*", s):
        s = s.lstrip("=+@")  # never keep spreadsheet formula text
    return s[:limit]
