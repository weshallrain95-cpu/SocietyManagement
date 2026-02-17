"""
SocietyOS System Registry
Central discovery and metadata system
"""

from typing import Dict, Any, List
from datetime import datetime


class RegistryRecord:
    """
    Single registry record
    """

    def __init__(self, name: str, category: str, obj: Any, metadata: Dict[str, Any] = None):
        self.name = name
        self.category = category
        self.obj = obj
        self.metadata = metadata or {}
        self.registered_at = datetime.utcnow().isoformat()

    def snapshot(self):
        return {
            "name": self.name,
            "category": self.category,
            "metadata": self.metadata,
            "registered_at": self.registered_at,
        }


class SystemRegistry:
    """
    Central registry for SocietyOS
    """

    def __init__(self):
        self.records: Dict[str, RegistryRecord] = {}

    # ---------- Core Registration ----------

    def register(self, name: str, category: str, obj: Any, metadata: Dict[str, Any] = None):
        key = f"{category}:{name}"
        self.records[key] = RegistryRecord(name, category, obj, metadata)

    # ---------- Discovery ----------

    def get(self, name: str, category: str):
        key = f"{category}:{name}"
        record = self.records.get(key)
        return record.obj if record else None

    def list_by_category(self, category: str) -> List[str]:
        return [
            record.name
            for record in self.records.values()
            if record.category == category
        ]

    def list_all(self) -> Dict[str, List[str]]:
        output: Dict[str, List[str]] = {}
        for record in self.records.values():
            output.setdefault(record.category, []).append(record.name)
        return output

    # ---------- Introspection ----------

    def snapshot(self):
        return {
            key: record.snapshot()
            for key, record in self.records.items()
        }

    def stats(self):
        stats: Dict[str, int] = {}
        for record in self.records.values():
            stats[record.category] = stats.get(record.category, 0) + 1
        return stats

