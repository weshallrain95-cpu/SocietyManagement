"""
==========================================================
SocietyOS Knowledge Center
Remove Active Focus
==========================================================
"""

from __future__ import annotations

import json
from pathlib import Path


DATA_DIRECTORY = Path(__file__).parent / "data"

CURRENT_FOCUS_FILE = (
    DATA_DIRECTORY / "current_focus.json"
)


def remove_focus(note_id: str) -> None:
    """
    Removes one note from the Active Focus board.

    The knowledge note itself is NOT deleted.
    """

    if CURRENT_FOCUS_FILE.exists():

        with open(
            CURRENT_FOCUS_FILE,
            "r",
            encoding="utf-8",
        ) as fp:

            try:

                focus_items = json.load(fp)

            except json.JSONDecodeError:

                focus_items = []

    else:

        focus_items = []

    focus_items = [

        item

        for item in focus_items

        if item["note_id"] != note_id

    ]

    with open(
        CURRENT_FOCUS_FILE,
        "w",
        encoding="utf-8",
    ) as fp:

        json.dump(
            focus_items,
            fp,
            indent=4,
            ensure_ascii=False,
        )