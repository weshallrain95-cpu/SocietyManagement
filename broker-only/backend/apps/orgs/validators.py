"""Indian business identifiers for broker registration: PAN, GSTIN (with its check character), MahaRERA agent no."""

import re

PAN_RE = re.compile(r"^[A-Z]{3}[ABCFGHLJPT][A-Z]\d{4}[A-Z]$")
GSTIN_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
RERA_AGENT_RE = re.compile(r"^A\d{11}$")

# The 4th letter of a PAN says who holds it; it must fit the ownership type.
PAN_HOLDER = {
    "individual": {"P"},
    "proprietorship": {"P"},  # a proprietorship is taxed on the proprietor's own PAN
    "partnership": {"F"},
    "llp": {"F"},  # LLPs are issued firm PANs
    "private_limited": {"C"},
    "public_limited": {"C"},
}
PAN_HOLDER_LABEL = {"P": "a person", "F": "a firm or LLP", "C": "a company"}

_GST_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def clean_id(value: str) -> str:
    return re.sub(r"[\s-]", "", value or "").upper()


def gstin_check_char(first14: str) -> str:
    total = 0
    for i, ch in enumerate(first14):
        v = _GST_CHARS.index(ch) * (2 if i % 2 else 1)
        total += v // 36 + v % 36
    return _GST_CHARS[(36 - total % 36) % 36]


def pan_problem(pan: str, ownership_type: str) -> str | None:
    if not PAN_RE.match(pan):
        return "PAN should look like ABCDE1234F (5 letters, 4 digits, 1 letter)."
    allowed = PAN_HOLDER.get(ownership_type)
    if allowed and pan[3] not in allowed:
        want = " or ".join(PAN_HOLDER_LABEL[x] for x in sorted(allowed))
        holder = PAN_HOLDER_LABEL.get(pan[3], "another kind of holder")
        kind = ownership_type.replace("_", " ")
        return f"This PAN belongs to {holder}, but the business is set up as {kind} (needs the PAN of {want})."
    return None


def gstin_problem(gstin: str, pan: str | None) -> str | None:
    if not GSTIN_RE.match(gstin):
        return "GSTIN should be 15 characters, like 27ABCDE1234F1Z5."
    if gstin_check_char(gstin[:14]) != gstin[14]:
        return "This GSTIN has a typo (its last character does not match)."
    if pan and gstin[2:12] != pan:
        return "The GSTIN does not contain this business's PAN. Check both numbers."
    return None
