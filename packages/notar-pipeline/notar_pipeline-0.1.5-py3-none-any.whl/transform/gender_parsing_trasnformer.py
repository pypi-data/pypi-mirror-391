import pandas as pd
from base import BaseTransformer


class TitleGenderTransformer(BaseTransformer):
    """
    Standardize legal/notary titles and extract gender.
    """

    def __init__(self):
        self.title_map = {
            "verwalter": "Notary Administrator",
            "abwickler": "Notary Liquidator",
            "notar": "Notary",
        }

    def _parse_title_gender(self, title: str) -> pd.Series:
        """Extract standardized title and gender from raw title."""
        if not isinstance(title, str) or title.strip() == "":
            return pd.Series([None, None])

        # Gender detection
        title_lower = title.lower()
        if any(word in title_lower for word in ["notarin", "verwalterin", "abwicklerin"]):
            gender = "F"
        else:
            gender = "M"

        # Base title standardization
        if "rechtsanwalt" in title_lower and "notar" in title_lower:
            base_title = "Attorney and Notary"
        elif "verwalter" in title_lower:
            base_title = "Notary Administrator"
        elif "abwickler" in title_lower:
            base_title = "Notary Liquidator"
        elif "notar" in title_lower:
            base_title = "Notary"
        else:
            base_title = title.strip()

        return pd.Series([base_title, gender])


    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df[["Standardized_Title", "Gender"]] = df["office_title"].apply(self._parse_title_gender)
        return df
