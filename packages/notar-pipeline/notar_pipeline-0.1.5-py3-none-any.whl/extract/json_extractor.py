import json
from base import BaseExtractor
class JSONExtractor(BaseExtractor):
    """Reads JSON file and returns list of records."""

    def extract(self, json_path: str) -> list[dict]:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
