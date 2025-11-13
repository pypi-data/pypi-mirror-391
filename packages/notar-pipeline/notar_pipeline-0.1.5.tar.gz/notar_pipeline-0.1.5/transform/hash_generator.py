import hashlib
import pandas as pd
from base import BaseTransformer
from transform.cleaning import CleaningTransformer


class HashGenerator(BaseTransformer):
    """
    Adds a hash column computed from given columns.
    """

    def __init__(self, cols: list[str], hash_col: str = "record_hash"):
        """
        Args:
            cols (list[str]): Columns to include in hash computation.
            hash_col (str): Name of the output hash column.
        """
        self.cols = cols
        self.hash_col = hash_col
        self.cleaner = CleaningTransformer()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute MD5 hash from specified columns and add it as a new column."""
        df = df.copy()

        # Normalize target columns using CleaningTransformer
        for c in self.cols:
            if c in df.columns:
                df[c] = df[c].map(self.cleaner._normalize_string)

        # Compute hash
        df[self.hash_col] = (
            df[self.cols]
            .astype(str)
            .apply(lambda row: hashlib.md5("|".join(row).encode("utf-8")).hexdigest(), axis=1)
        )

        # Replace empty strings with None
        df.replace(r'^\s*$', None, regex=True, inplace=True)

        return df
