import hashlib
import pandas as pd
from base import BaseTransformer


class IDGenerator(BaseTransformer):
    """Generates deterministic relationship IDs for relationship tables."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add a deterministic relationship_id column."""
        if df.empty:
            return df

        df = df.copy()
        df["relationship_id"] = df.apply(
            lambda row: hashlib.md5(
                f"{row.get('parent_notary_id', '')}|"
                f"{row.get('related_notary_id', '')}|"
                f"{row.get('relation_type', '')}|"
                f"{row.get('valid_from', '')}|"
                f"{row.get('valid_to', '')}".encode("utf-8")
            ).hexdigest(),
            axis=1
        )
        return df
