"""Name and unit-number normalisation (Data Model §5.2).

Pure functions, no database access, heavily unit-tested: this is what stops
"Hira Nandani Est.", "Hiranandani Estate" and "HIRANANDANI ESTATE CHS" from
becoming three different societies.
"""
import re
import unicodedata
from dataclasses import dataclass, field

# Abbreviations and spelling variants -> canonical token.
EXPANSIONS = {
    "est": "estate", "estt": "estate", "encl": "enclave", "encl.": "enclave", "hts": "heights", "ht": "heights",
    "apt": "apartment", "apts": "apartment", "appt": "apartment", "apartments": "apartment", "aptmt": "apartment",
    "bldg": "building", "bldgs": "building", "blds": "building", "bld": "building", "buildings": "building",
    "twr": "tower", "twrs": "tower", "towers": "tower", "resi": "residency", "res": "residency",
    "residences": "residency", "residence": "residency", "cplx": "complex", "comp": "complex",
    "soc": "society", "socy": "society", "sty": "society", "nagr": "nagar", "ngr": "nagar",
    "pk": "park", "gdn": "garden", "gdns": "garden", "gardens": "garden", "vly": "valley", "vihar": "vihar",
    "chsl": "chs", "c.h.s": "chs", "c.h.s.": "chs", "c.h.s.l": "chs", "cghs": "chs",
    "phs": "phase", "ph": "phase", "sec": "sector", "sect": "sector", "no": "", "rd": "road", "mg": "mg",
    "ext": "extension",
    # Common Devanagari-transliteration spellings.
    "istet": "estate", "estet": "estate", "isteit": "estate", "sosaiti": "society", "sosayati": "society",
    "sosaayatee": "society", "apaartament": "apartment", "apartament": "apartment", "tavar": "tower", "taavar": "tower",
    "paark": "park", "haits": "heights", "rejidensi": "residency", "rejeedensee": "residency", "extn": "extension", "st": "saint",
}
# Multi-word legal suffixes collapsed before tokenising.
PHRASES = [
    (r"co[\s\-]*op(erative)?\.?\s*(hsg|housing)\.?\s*(soc(iety)?|sty)\.?\s*(ltd|limited)?\.?", " chs "),
    (r"housing\s+society(\s+ltd)?", " chs "),
    (r"\bpvt\.?\s*ltd\.?|\bprivate\s+limited\b|\bltd\.?\b|\blimited\b", " "),
]
# Generic words: kept, but carry little identity (weak tokens).
WEAK = {
    "chs", "society", "apartment", "building", "tower", "heights", "residency", "complex", "estate", "enclave",
    "park", "nagar", "garden", "phase", "sector", "the", "and", "of", "new", "old", "co", "op", "hsg", "valley",
    "palace", "plaza", "villa", "villas", "homes", "home", "city", "township", "court", "castle", "mansion",
    "road", "marg", "lane", "niwas", "sadan", "bhavan", "bhawan", "kunj", "dham", "vihar", "angan", "wing", "block", "bldg",
}
# Locality words commonly appended to names in broker sheets (pilot + neighbours).
LOCALITY_WORDS = {
    "thane", "thane west", "thane w", "ghodbunder", "ghodbunder road", "gb road", "g b road", "dhokali", "manpada",
    "kolshet", "majiwada", "kapurbawdi", "kasarvadavali", "owale", "waghbil", "patlipada", "vasant vihar",
    "pokhran", "pokhran road", "hiranandani meadows", "balkum", "wagle estate", "naupada", "panchpakhadi",
    "mumbai", "navi mumbai", "kalyan", "dombivli", "kharghar", "ulwe", "panvel",
}
_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_WING = re.compile(
    r"\b(?:(?P<a>[a-z])\s*[-/]?\s*(?:wing|wg|wng|block|blk))\b|\b(?:wing|block|tower|twr|bldg|building)\s*(?:no\.?\s*)?(?P<b>[a-z0-9]{1,3})\b"
)


@dataclass
class NormalisedName:
    text: str
    tokens: list[str]
    strong: list[str]
    locality_hint: str = ""
    building_hint: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def compact(self) -> str:
        return "".join(self.tokens)

    @property
    def strong_compact(self) -> str:
        return "".join(self.strong)

    @property
    def skeleton(self) -> str:
        return skeleton(self.strong_compact or self.compact)


def _fold(raw: str) -> str:
    s = unicodedata.normalize("NFKC", raw or "").lower()
    if _DEVANAGARI.search(s):
        s = _transliterate_devanagari(s)
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def normalise_name(raw: str) -> NormalisedName:
    s = _fold(raw)
    s = s.replace("&", " and ")
    for pattern, repl in PHRASES:
        s = re.sub(pattern, repl, s)

    building_hint = ""
    m = _WING.search(s)
    if m:
        building_hint = (m.group("a") or m.group("b") or "").upper()
        s = s[: m.start()] + " " + s[m.end():]

    s = re.sub(r"[^\w\s]", " ", s)
    expanded = []
    for t in s.split():
        t = EXPANSIONS.get(t, t)
        if t:
            expanded.append(t)
    s = " ".join(expanded)

    locality_hint = ""
    for loc in sorted(LOCALITY_WORDS, key=len, reverse=True):
        if re.search(rf"(^|\s){re.escape(loc)}($|\s)", s) and s != loc:
            # Only strip a trailing/embedded locality when something remains as the name.
            remainder = re.sub(rf"(^|\s){re.escape(loc)}($|\s)", " ", s).strip()
            if remainder:
                locality_hint = locality_hint or loc
                s = remainder

    tokens = s.split()
    # Split brand words ("hira nandani" vs "hiranandani") are handled by comparing compact forms downstream.
    strong = [t for t in tokens if t not in WEAK and not t.isdigit()]
    return NormalisedName(
        text=" ".join(tokens), tokens=tokens, strong=strong, locality_hint=locality_hint, building_hint=building_hint
    )


def skeleton(s: str) -> str:
    """Phonetic-ish key: folds vowel length, doubled letters and common Indian spelling swaps."""
    s = re.sub(r"[^a-z0-9]", "", s.lower())
    for a, b in (("aa", "a"), ("ee", "i"), ("oo", "u"), ("w", "v"), ("ph", "f"), ("sh", "s"), ("z", "j"), ("y", "i")):
        s = s.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", s)


def normalise_building(raw: str) -> str:
    s = _fold(raw)
    s = re.sub(r"\b(wing|wg|block|blk|tower|twr|building|bldg|no)\b\.?", " ", s)
    s = re.sub(r"[^\w]", "", s).upper()
    return s or "MAIN"


@dataclass
class UnitNo:
    unit_no: str
    floor: int | None
    wing: str = ""


_FLOOR_WORD = re.compile(r"(\d{1,3})\s*(?:st|nd|rd|th)?\s*(?:floor|flr|fl)\b", re.I)


def normalise_unit_no(raw: str) -> UnitNo:
    """'B-1203' -> (1203, floor 12, wing B); 'Flat 1203, 12th flr' -> (1203, 12); '12/03' -> (1203, 12); 'G-2' -> (G2, 0)."""
    s = _fold(raw).strip()
    floor = None
    fm = _FLOOR_WORD.search(s)
    if fm:
        floor = int(fm.group(1))
        s = s[: fm.start()] + s[fm.end():]
    s = re.sub(r"\b(flat|flt|unit|room|rm|shop|no|number|apt|apartment)\b\.?", " ", s)
    wing = ""
    wm = re.match(r"^\s*([a-z])\s*(?:wing)?\s*[-/ ]\s*(\d{2,4})\b", s) or re.match(r"^\s*([a-z])(\d{3,4})\b", s)
    if wm:
        wing, s = wm.group(1).upper(), wm.group(2)
    sm = re.fullmatch(r"\s*(\d{1,3})\s*/\s*(\d{1,2})\s*", s)
    if sm:  # floor/flat style "12/03"
        floor = floor if floor is not None else int(sm.group(1))
        s = f"{int(sm.group(1))}{int(sm.group(2)):02d}"
    s = re.sub(r"[^\w]", "", s).upper()
    if s.startswith("G") and s[1:].isdigit():
        floor = 0 if floor is None else floor
    elif floor is None and s.isdigit() and len(s) >= 3:
        floor = int(s[:-2])
    return UnitNo(unit_no=s or "?", floor=floor, wing=wing)


# Minimal Devanagari -> Latin transliteration (Marathi/Hindi names in broker sheets).
_DV_VOWELS = {"अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au", "ऋ": "ru"}
_DV_SIGNS = {"ा": "aa", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo", "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "ृ": "ru", "ं": "n", "ः": "h", "ँ": "n"}
_DV_CONS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n", "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "n",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n", "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m", "य": "y", "र": "r", "ल": "l", "ळ": "l", "व": "v",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
}
_DV_DIGITS = {chr(0x0966 + i): str(i) for i in range(10)}


def _transliterate_devanagari(s: str) -> str:
    out = []
    chars = list(s)
    for i, c in enumerate(chars):
        nxt = chars[i + 1] if i + 1 < len(chars) else ""
        if c in _DV_CONS:
            out.append(_DV_CONS[c])
            if nxt not in _DV_SIGNS and nxt != "्" and nxt and nxt not in " \t" and "ऀ" <= nxt <= "ॿ":
                out.append("a")
        elif c in _DV_VOWELS:
            out.append(_DV_VOWELS[c])
        elif c in _DV_SIGNS:
            out.append(_DV_SIGNS[c])
        elif c == "्":
            continue
        elif c in _DV_DIGITS:
            out.append(_DV_DIGITS[c])
        else:
            out.append(c)
    return "".join(out)
