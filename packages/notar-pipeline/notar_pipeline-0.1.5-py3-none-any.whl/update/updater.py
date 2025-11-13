import os
import pandas as pd
from datetime import datetime

class Updater:
    """
    Führt eine inkrementelle Historisierung (SCD Type 2) anhand eines Hash-Werts durch.
    """

    def __init__(self, historical_path: str, unique_key: str, hash_col= "record_hash"):
        self.historical_path = historical_path
        self.unique_key = unique_key
        self.hash_col = hash_col

    def _load_existing(self) -> pd.DataFrame:
        if os.path.exists(self.historical_path):
            df = pd.read_parquet(self.historical_path)
            print(f"Historische Datensätze geladen: {len(df)}")
            return df
        else:
            print("Noch keine Historie vorhanden. Neue Datei wird erstellt.")
            return pd.DataFrame()

    def update(self, df_new: pd.DataFrame) -> pd.DataFrame:
        df_hist = self._load_existing()
        now = pd.Timestamp.now().normalize()

        if df_hist.empty:
            df_new = df_new.copy()
            df_new["valid_from"] = now
            df_new["valid_to"] = pd.NaT
            df_new["is_current"] = True
            os.makedirs(os.path.dirname(self.historical_path), exist_ok=True)
            df_new.to_parquet(self.historical_path, index=False)
            print(f"{len(df_new)} initiale Datensätze gespeichert.")
            return df_new

        # Nur aktuelle Versionen betrachten
        df_current = df_hist[df_hist["is_current"] == True].copy()

        # Merge mit alten Hashes
        merged = df_new.merge(
            df_current[[self.unique_key, self.hash_col]],
            on=self.unique_key,
            how="left",
            suffixes=("_new", "_old")
        )

        # 🧩 Nur die "_new"-Spalten zurückbenennen
        cols_new = [c for c in merged.columns if c.endswith("_new")]
        merged.rename(columns={c: c.replace("_new", "") for c in cols_new}, inplace=True)

        # Neue Datensätze
        new_records = merged[merged[self.hash_col + "_old"].isna()][df_new.columns].copy()
        new_records["valid_from"] = now
        new_records["valid_to"] = pd.NaT
        new_records["is_current"] = True

        # Geänderte Datensätze
        changed_records = merged[
            merged[self.hash_col + "_old"].notna() &
            (merged[self.hash_col] != merged[self.hash_col + "_old"])
        ][df_new.columns].copy()
        changed_records["valid_from"] = now
        changed_records["valid_to"] = pd.NaT
        changed_records["is_current"] = True

        # Alte Versionen schließen
        ids_changed = changed_records[self.unique_key].unique().tolist()
        df_hist.loc[
            (df_hist[self.unique_key].isin(ids_changed)) & (df_hist["is_current"]),
            ["valid_to", "is_current"]
        ] = [now, False]

        # Zusammenführen
        df_final = pd.concat([df_hist, new_records, changed_records], ignore_index=True)
        os.makedirs(os.path.dirname(self.historical_path), exist_ok=True)
        df_final.to_parquet(self.historical_path, index=False)

        print(f" Neu: {len(new_records)} | Geändert: {len(changed_records)} | Gesamt: {len(df_final)}")
        return df_final
