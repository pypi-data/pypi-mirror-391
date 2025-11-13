import pandas as pd
from base import BaseTransformer


class NameTransformer(BaseTransformer):
    """Combines title, first name, and last name into a clean NotaryName field."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Hilfsfunktion zur Namenskombination
        def _combine_name(row):
            parts = [
                str(row.get("office_title", "")).strip(),
                str(row.get("firstname", "")).strip(),
                str(row.get("lastname", "")).strip(),
            ]
            # Nur nicht-leere Teile kombinieren
            name = " ".join(p for p in parts if p)
            # Mehrfache Leerzeichen entfernen
            name = " ".join(name.split())
            return name or None

        df["NotaryName"] = df.apply(_combine_name, axis=1)

        return df
