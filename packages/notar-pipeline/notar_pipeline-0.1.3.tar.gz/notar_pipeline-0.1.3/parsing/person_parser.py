from base import BaseParser


class PersonParser(BaseParser):

    def parse(self, notar: dict) -> dict:

        d = notar.get("resultList", {}) or {}

        return {
            "personId": d.get("personId"),
            "userId": d.get("userId"),
            "firstName": d.get("firstName"),
            "lastName": d.get("lastName"),
            "title": d.get("title"),
            "valid_from": d.get("validFrom"),
            "valid_to": d.get("validTo"),
        }