import json
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"


def load_knowledge():
    """
    Loads every JSON file from the Knowledge Center data folder.

    Returns:

        {
            "architecture_decisions": [...],
            "architecture_notes": [...],
            ...
        }

    Any new JSON file added to /data automatically becomes
    available without changing backend code.
    """

    knowledge = {}

    for json_file in sorted(DATA_DIR.glob("*.json")):

        key = json_file.stem

        try:

            with open(json_file, "r", encoding="utf-8") as f:

                knowledge[key] = json.load(f)

        except json.JSONDecodeError:

            knowledge[key] = {
                "error": f"{json_file.name} contains invalid JSON."
            }

        except Exception as exc:

            knowledge[key] = {
                "error": str(exc)
            }

    
    return knowledge