"""
==========================================================
SocietyOS Knowledge Center
Knowledge Persistence Engine
==========================================================

Single Responsibility

Append one knowledge note into one JSON repository.

No Django.

No HTTP.

No API.

Pure persistence only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


DATA_DIRECTORY = Path(__file__).parent / "data"


CATEGORY_FILES = {

    "architecture_decisions": "architecture_decisions.json",

    "architecture_notes": "architecture_notes.json",

    "product_principles": "product_principles.json",

    "future_engines": "future_engines.json",

    "current_reconstruction": "current_reconstruction.json",

}

PREFIX_MAP = {

    "architecture_decisions": "AD",

    "architecture_notes": "AN",

    "product_principles": "PP",

    "future_engines": "FE",

    "current_reconstruction": "CR",

}


def generate_note_id(category: str, existing_notes: list) -> str:
    """
    Generates the next knowledge identifier.

    Example

    AD-0001
    AD-0002
    AD-0003
    """

    prefix = PREFIX_MAP[category]

    return f"{prefix}-{len(existing_notes) + 1:04d}"


def save_note(*, category: str, note: Dict) -> Dict:
    """
    Appends one note into the selected repository.

    Returns
    -------
    Saved note.
    """

    if category not in CATEGORY_FILES:

        raise ValueError(
            f"Unknown knowledge category: {category}"
        )

    file_path = DATA_DIRECTORY / CATEGORY_FILES[category]

    if file_path.exists():

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as fp:

            try:

                data = json.load(fp)

            except json.JSONDecodeError:

                data = []

    else:

        data = []

    note["id"] = generate_note_id(
        category,
        data,
    )

    data.append(note)

    if note.get("makeCurrentFocus"):

        current_focus_file = (
            DATA_DIRECTORY / "current_focus.json"
        )

        if current_focus_file.exists():

            with open(
                current_focus_file,
                "r",
                encoding="utf-8",
            ) as fp:

                try:

                    current_focus = json.load(fp)

                except json.JSONDecodeError:

                    current_focus = []

        else:

            current_focus = []

        current_focus.append({

            "note_id": note["id"],

            "title": note["title"],

            "category": category,

        })

        with open(
            current_focus_file,
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                current_focus,
                fp,
                indent=4,
                ensure_ascii=False,
            )

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as fp:

        json.dump(
            data,
            fp,
            indent=4,
            ensure_ascii=False,
        )

    return note