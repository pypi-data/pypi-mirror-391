import pandas as pd
from base import BaseTransformer

class DateNormalizer(BaseTransformer):
    """Normalizes date columns into YYYY-MM-DD format, handling timezone-aware values."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in ["valid_from", "valid_to"]:
            if col in df.columns:
                df[col] = (
                    pd.to_datetime(df[col], errors="coerce", utc=True)  # <-- wichtig!
                    .dt.tz_convert(None)                                # <-- entfernt +01:00
                    .dt.strftime("%Y-%m-%d")
                )
                df[col] = df[col].where(df[col].notnull(), None)
        return df
