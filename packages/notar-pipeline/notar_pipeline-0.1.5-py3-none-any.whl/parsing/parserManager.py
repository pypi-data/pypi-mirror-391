import os
import pandas as pd

from parsing.notar_parser import NotarParser
from parsing.person_parser import PersonParser
from parsing.chamber_parser import ChamberParser
from parsing.relationships_parser import RelationshipsParser


class ParserManager:
    """Manages all parsers and executes the parsing process (raw only)."""

    def __init__(self):
        # Jeder Parser arbeitet unabhängig
        self.parsers = {
            "notars": NotarParser(),
            "persons": PersonParser(),
            "chambers": ChamberParser(),
            "relationships": RelationshipsParser(),
        }

    def parse_all(self, raw_data):
        """Parses all data and returns dict of raw DataFrames (1:1)."""
        parsed_data = {}

        for name, parser in self.parsers.items():
            print(f"Parsing {name} ...")

            parsed_rows = [parser.parse(record) for record in raw_data]

            if name == "relationships":
                # Flatten der verschachtelten Listen
                parsed_rows = [r for sublist in parsed_rows for r in sublist]

            df = pd.DataFrame(parsed_rows)
            parsed_data[name] = df

            print(f"{name}: {len(df)} Zeilen, {len(df.columns)} Spalten")

        return parsed_data

    def save_parsed_data(self, parsed_data: dict, output_dir: str):
        """Saves each parsed DataFrame as a CSV file (no transformations)."""
        os.makedirs(output_dir, exist_ok=True)

        for name, df in parsed_data.items():
            path = os.path.join(output_dir, f"{name}.csv")
            df.to_csv(path, index=False, encoding="utf-8")
            print(f"{name}.csv gespeichert ({len(df)} Zeilen, {len(df.columns)} Spalten)")
