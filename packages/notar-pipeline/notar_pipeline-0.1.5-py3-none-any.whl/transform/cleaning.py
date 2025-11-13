import pandas as pd
import numpy as np
from base import BaseTransformer

class CleaningTransformer(BaseTransformer):
    """Cleans empty strings, normalizes None/nan values, and trims strings."""

    def _normalize_string(self, s):
        """Trim whitespace and replace special characters like \\xa0."""
        # Handle lists or arrays first
        if isinstance(s, (list, np.ndarray)):
            if len(s) == 0:
                return None
            s = s[0]

        if s is None or (isinstance(s, float) and np.isnan(s)) or pd.isna(s):
            return None

        if isinstance(s, str):
            s = s.strip().replace("\xa0", " ")
            return s if s != "" else None

        return str(s)


    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply cleaning to all string columns."""
        df = df.copy()

        # Replace empty-like strings with NaN
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

        # Fix: Move (?i) to start for case-insensitive replacement
        df.replace(r'(?i)^(none|nan)$', np.nan, regex=True, inplace=True)

        # Convert NaN to None (for SQL compatibility)
        df.where(pd.notnull(df), None, inplace=True)

        # Normalize string columns
        for col in df.select_dtypes(include=["object", "string"]).columns:
            df[col] = df[col].map(self._normalize_string)

        return df
