from base import BaseParser


class RelationshipsParser(BaseParser):
    """
    Parser für Notar-Beziehungen (Identität, Amtstätigkeit, Aktenverwahrung, Pillions).
    """

    def parse(self, notar: dict) -> list[dict]:
        relationships = []

        # --- Basisinformationen ---
        details = notar.get("details", {})
        d = details.get("notar", {}) or {}
        parent_id = d.get("id")
        parent_person_id = notar.get("resultList", {}).get("personId")

        # --- Identität ---
        if parent_id and parent_person_id:
            relationships.append({
                "parent_notary_id": parent_id,
                "parent_personId": parent_person_id,
                "related_notary_id": parent_id,
                "related_personId": parent_person_id,
                "relation_type": "Same",
                "office_name": d.get("officeName"),
                "storage_comment": None,
                "valid_from": (d.get("notaryValidity") or {}).get("from") or d.get("validFrom"),
                "valid_to": (d.get("notaryValidity") or {}).get("to") or d.get("validTo"),
            })

        # --- Amtstätigkeit ---
        for a in details.get("amtstaetigkeit", []) or []:
            validity = a.get("notaryValidity") or {}
            relationships.append({
                "parent_notary_id": parent_id,
                "parent_personId": parent_person_id,
                "related_notary_id": a.get("storageNotaryId"),
                "related_personId": None,
                "relation_type": "amtstaetigkeit",
                "office_name": a.get("officeName"),
                "storage_comment": a.get("storageName"),
                "valid_from": validity.get("from") or a.get("validFrom") or a.get("from"),
                "valid_to": validity.get("to") or a.get("validTo") or a.get("to"),
            })

        # --- Aktenverwahrung ---
        for a in details.get("aktenverwahrung", []) or []:
            validity = a.get("recordPeriod") or {}
            relationships.append({
                "parent_notary_id": parent_id,
                "parent_personId": parent_person_id,
                "related_notary_id": a.get("notaryId"),
                "related_personId": None,
                "relation_type": "aktenverwahrung",
                "office_name": a.get("officeName"),
                "storage_comment": a.get("storageComment"),
                "valid_from": validity.get("from") or a.get("from"),
                "valid_to": validity.get("to") or a.get("to"),
            })

        # --- Pillions ---
        for p in d.get("pillions", []) or []:
            validity = p.get("notaryValidity") or {}
            relationships.append({
                "parent_notary_id": parent_id,
                "parent_personId": parent_person_id,
                "related_notary_id": p.get("id"),
                "related_personId": p.get("personId"),
                "relation_type": "pillion",
                "office_name": p.get("officeName"),
                "storage_comment": None,
                "valid_from": validity.get("from") or p.get("validFrom"),
                "valid_to": validity.get("to") or p.get("validTo"),
            })

        return relationships
