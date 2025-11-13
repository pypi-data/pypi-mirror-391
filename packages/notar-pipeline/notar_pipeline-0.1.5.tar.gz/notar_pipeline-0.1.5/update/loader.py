import os
import pandas as pd

class ParquetLoader:
    """
    Lädt die aktuellste oder alle Parquet-Dateien aus einem Verzeichnis.
    """

    def __init__(self, raw_path: str):
        self.raw_path = raw_path

    def _get_parquet_files(self):
        return [
            os.path.join(self.raw_path, f)
            for f in os.listdir(self.raw_path)
            if f.endswith(".parquet")
        ]

    def load_latest(self) -> pd.DataFrame:
        files = self._get_parquet_files()
        if not files:
            raise FileNotFoundError(f"Keine Parquet-Dateien gefunden unter {self.raw_path}")

        latest_file = max(files, key=os.path.getmtime)
        print(f"Lade aktuellste Datei: {os.path.basename(latest_file)}")
        return pd.read_parquet(latest_file)

    def load_all(self) -> list[pd.DataFrame]:
        files = self._get_parquet_files()
        if not files:
            raise FileNotFoundError(f"Keine Parquet-Dateien gefunden unter {self.raw_path}")

        print(f"Lade {len(files)} Dateien aus {self.raw_path}")
        return [pd.read_parquet(f) for f in files]
