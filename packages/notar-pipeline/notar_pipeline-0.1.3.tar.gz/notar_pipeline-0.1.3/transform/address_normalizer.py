import re
import pandas as pd
from base import BaseTransformer

class AddressNormalizer(BaseTransformer):
    """Splits an address string into 'street_name' and 'house_number'."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if "address" not in df.columns:
            return df  # skip if not applicable

        df = df.copy()

        def split_address(addr):
            if not isinstance(addr, str) or not addr.strip():
                return (None, None)
            m = re.match(r'^(.*?)(\d+\w*)$', addr.strip())
            return (m.group(1).strip(), m.group(2).strip()) if m else (addr.strip(), None)

        # unpack result into two new columns
        df[["street_name", "house_number"]] = pd.DataFrame(
            df["address"].apply(split_address).tolist(), index=df.index
        )
        return df
