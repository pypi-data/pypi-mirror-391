import os
import re
import pandas as pd
from base import BaseTransformer
from dotenv import load_dotenv

load_dotenv()

class PhoneNormalizer(BaseTransformer):
    """Normalisiert deutsche Telefonnummern und erzeugt lesbare Schreibweise."""

    def __init__(self):
        prefix_path = os.getenv("PHONE_PREFIX_PATH")
        if not prefix_path:
            raise ValueError("PHONE_PREFIX_PATH not set in environment.")

        df = pd.read_excel(prefix_path, dtype=str)
        self.prefixes = sorted(
            {re.sub(r"[^\d]", "", str(v)).lstrip("0") for v in df.iloc[:, 0]},
            key=len, reverse=True
        )

    def _normalize(self, val: str):
        if not isinstance(val, str) or not val.strip():
            return None
        s = re.sub(r"[^\d+]", "", val)
        s = re.sub(r"^\+490+", "+49", s)
        if s.startswith("+49"): return s
        if s.startswith("00"):  return "+" + s[2:]
        if s.startswith("0"):   return "+49" + s[1:]
        return s

    def _split(self, num: str):
        if not num or not num.startswith("+49"):
            return (None, None)
        s = num.removeprefix("+49")
        for p in self.prefixes:
            if s.startswith(p):
                return (p, s[len(p):])
        return (None, s)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if "phone" not in df.columns:
            return df

        df = df.copy()
        df["phone_norm"] = df["phone"].apply(self._normalize)

        # Prefix + Subscriber extrahieren
        df[["prefix_matched", "subscriber_number"]] = pd.DataFrame(
            df["phone_norm"].apply(self._split).tolist(), index=df.index
        )

        # Kompakte lesbare Form
        df["phone_norm"] = df.apply(
            lambda r: f"+49(0){r.prefix_matched}/{r.subscriber_number}"
            if pd.notna(r.prefix_matched) and pd.notna(r.subscriber_number)
            else r.phone_norm,
            axis=1
        )
        return df
