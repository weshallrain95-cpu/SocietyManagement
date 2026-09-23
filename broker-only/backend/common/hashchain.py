"""Canonical hashing shared by the audit log and the unit status ledger."""

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

GENESIS = "0" * 64


def _default(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, (UUID, Decimal)):
        return str(o)
    raise TypeError(type(o))


def canonical(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=_default, ensure_ascii=False)


def chain_hash(prev_hash: str, data: dict) -> str:
    return hashlib.sha256((prev_hash + canonical(data)).encode()).hexdigest()
