import json
import os
from typing import Any

class ActionsFileHelper:
    """Helper for loading JSON/text content from the actions folder for tests."""
    @staticmethod
    def get_json(filename: str) -> dict[str, Any]:
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, '..', 'actions', filename)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def get_text(filename: str) -> str:
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, '..', 'actions', filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
