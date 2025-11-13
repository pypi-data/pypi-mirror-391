import re
import pandas as pd
from base import BaseTransformer


class AddressNormalizer(BaseTransformer):

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if "address" not in df.columns:
            return df

        df = df.copy()

        def split_address(addr: str):
            if not isinstance(addr, str) or not addr.strip():
                return (None, None, None)
            addr = addr.strip()

            # Versuch, Straße + Hausnummer(n) zu trennen
            pattern = r"^(.*?)(\d{1,4})([A-Za-z]?)([-/]\d+[A-Za-z/]*)?\s*$"
            # Beispiel-Gruppen:
            # 1: Straße
            # 2: Nummer
            # 3: einzelner Buchstabe direkt nach Nummer (z. B. 'A' in '8A')
            # 4: Bereich oder Zusatz (z. B. '-99' oder '/B')

            m = re.match(pattern, addr)
            if m:
                street = m.group(1).strip()
                number = m.group(2).strip() if m.group(2) else None
                suffix_letter = m.group(3).strip() if m.group(3) else None
                addition = m.group(4).strip() if m.group(4) else None

                # Kombiniere mögliche Zusatzteile
                hnr_add = None
                if suffix_letter and addition:
                    hnr_add = f"{suffix_letter}{addition}"
                elif suffix_letter:
                    hnr_add = suffix_letter
                elif addition:
                    hnr_add = addition

                return (street, number, hnr_add)

            # kein Match → reine Straße oder leer
            return (addr, None, None)

        df[["STREET", "HNR", "HNRADD"]] = pd.DataFrame(
            df["address"].apply(split_address).tolist(), index=df.index
        )
        return df
