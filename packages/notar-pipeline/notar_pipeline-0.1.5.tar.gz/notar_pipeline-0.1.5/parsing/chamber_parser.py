from base import BaseParser


class ChamberParser(BaseParser):


    def parse(self, notar: dict) -> dict:
        
        d = notar.get("details", {}).get("notar", {}) or {}

        return {
            "chamber_id": d.get("notaryChamberId"),
            "chamber_name": d.get("notaryChamberDesc"),
            "chamber_region": notar.get("chamberRegion"),
            "chamber_logo": d.get("notaryChamberLogo"),
        }