import os
import json
import logging
import pandas as pd
from typing import Dict, Any

# Importiere deine Basis- und Unter-Transformer
from base import BaseTransformer
from transform.cleaning import CleaningTransformer
from transform.date_transformer import DateNormalizer
from transform.address_normalizer import AddressNormalizer
from transform.phone_normalizer import PhoneNormalizer
from transform.gender_parsing_trasnformer import TitleGenderTransformer
from transform.url_transformer import URLNormalizer
from transform.id_generator import IDGenerator
from transform.hash_generator import HashGenerator
from transform.birthnameExtractor import BirthnameExtractor
from transform.geo_transfromer import GeoTransformer
from transform.language_transformer import LanguageTransformer
from transform.name_transformer import NameTransformer

class TransformPipeline:
    """Einfache JSON-gesteuerte Pipeline, die Parquet-Dateien lädt, transformiert und speichert."""

    def __init__(self, config_path: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        with open(config_path, "r", encoding="utf-8") as f:
            self.config: Dict[str, Any] = json.load(f)

        # Registry mit allen verfügbaren Transformern
        self.registry: Dict[str, BaseTransformer] = {
            "CleaningTransformer": CleaningTransformer(),
            "DateNormalizer": DateNormalizer(),
            "AddressNormalizer": AddressNormalizer(),
            "PhoneNormalizer": PhoneNormalizer(),
            "TitleGenderTransformer": TitleGenderTransformer(),
            "URLNormalizer": URLNormalizer(),
            "IDGenerator": IDGenerator(),
            "BirthnameExtractor": BirthnameExtractor(),
            "GeoTransformer": GeoTransformer(),
            "LanguageTransformer": LanguageTransformer(),
            "NameTransformer": NameTransformer()
        }

    # -------------------------------------------------------------
    def _apply(self, entry: Dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
        """Wendet einen einzelnen Transformer auf das DataFrame an."""
        name = entry["name"]
        cols = entry.get("columns")

        transformer = HashGenerator(cols) if name == "HashGenerator" else self.registry.get(name)
        if transformer is None:
            print(f"⚠️  Transformer '{name}' unbekannt – übersprungen.")
            return df

        print(f"➡️  Wende {name} an (Spalten: {cols or 'ALLE'})")
        return transformer.safe_transform(df)

    # -------------------------------------------------------------
    def transform(self, table_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Führt globale + tabellenspezifische Transformationen laut Config aus."""
        print(f"\n🔧 Transformiere Tabelle: {table_name}")

        # Globale Transformer
        for entry in self.config.get("global_transformers", []):
            df = self._apply(entry, df)

        # Tabellenspezifische Transformer
        table_conf = self.config.get("tables", {}).get(table_name, {})
        for entry in table_conf.get("transformers", []):
            df = self._apply(entry, df)

        print(f"✅ Fertig: {table_name}")
        return df

        # -------------------------------------------------------------
    def run(self, input_dir: str, output_dir: str):
        """Liest alle CSV-Dateien aus input_dir, transformiert sie und speichert sie in output_dir."""
        print(f"\n Starte Transformation:")
        print(f"Quelle: {input_dir}")
        print(f"Ziel:   {output_dir}")

        csv_files = [f for f in os.listdir(input_dir) if f.endswith(".csv")]
        if not csv_files:
            print(" Keine CSV-Dateien gefunden.")
            return

        os.makedirs(output_dir, exist_ok=True)

        for file in csv_files:
            table_name = os.path.splitext(file)[0]
            file_path = os.path.join(input_dir, file)

            print(f"\n Lade {file} ...")
            df = pd.read_csv(file_path)

            df_transformed = self.transform(table_name, df)

            out_path = os.path.join(output_dir, f"{table_name}_transformed.parquet")
            df_transformed.to_parquet(out_path, index=False)
            print(f"Gespeichert: {out_path} ({len(df_transformed)} Zeilen)")

        print("\nAlle Dateien erfolgreich transformiert.")
