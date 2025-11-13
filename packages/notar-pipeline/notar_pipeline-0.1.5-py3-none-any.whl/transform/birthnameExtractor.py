import re
from base import BaseTransformer


class BirthnameExtractor(BaseTransformer):
    """Extrahiert den Geburtsnamen (nach 'früher') aus einer Textspalte."""

    def __init__(self, source_column="office_name", target_column="Birthname"):
        """
        :param source_column: Name der Spalte, aus der der Geburtsname extrahiert wird
        :param target_column: Name der neuen Spalte, in der der Geburtsname gespeichert wird
        """
        self.source_column = source_column
        self.target_column = target_column

    def transform(self, df):
        df = df.copy()

        def _extract_birthname(text: str):
            if not isinstance(text, str):
                return None
            match = re.search(r"früher\s+([^,]+)", text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            return None

        df[self.target_column] = df[self.source_column].apply(_extract_birthname)
        return df
