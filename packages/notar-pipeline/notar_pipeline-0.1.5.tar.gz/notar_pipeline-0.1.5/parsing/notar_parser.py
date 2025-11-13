from base import BaseParser


class NotarParser(BaseParser):
    """Parst ein Roh-Notar-Objekt in ein flaches dict (keine DataFrame-Operationen)."""

    def parse(self, notar: dict) -> dict:
        d = notar.get("details", {}).get("notar", {}) or {}
        r = notar.get("resultList", {}) or {}

        return {
            "notar_id": d.get("id"),
            "person_id": r.get("personId"),
            "chamber_id": d.get("notaryChamberId"),
            "firstname": d.get("firstname"),
            "lastname": d.get("lastname"),
            "office_name": d.get("officeName"),
            "office_title": d.get("officeTitle"),
            "title": r.get("title"),
            "official_location": d.get("office"),
            "language1": d.get("language1"),
            "language2": d.get("language2"),
            "address": d.get("street"),
            "zip_code": d.get("zip"),
            "city": d.get("city"),
            "phone": d.get("phone"),
            "email": d.get("email"),
            "fax": d.get("fax"),
            "url": d.get("url"),
            "latitude": d.get("latitude"),
            "longitude": d.get("longitude"),
            "valid_from": d.get("validFrom"),
            "valid_to": d.get("validTo"),
        }


