import pandas as pd
from base import BaseTransformer


class LanguageTransformer(BaseTransformer):
    """Kombiniert Sprachspalten in eine einheitliche Spalte mit eindeutigen Sprachcodes."""

    def __init__(self, source_columns= ["language1", "language2"], target_column="languages", sort=True):
        """
        :param source_columns: Liste der Spaltennamen, die zusammengeführt werden sollen)
        """
        self.source_columns = source_columns
        self.target_column = target_column
        self.sort = sort

    def transform(self, df):
        df = df.copy()

        def _combine_languages(row):
            langs = set()
            for col in self.source_columns:
                val = row.get(col)
                if pd.notna(val):
                    parts = [x.strip() for x in val.split(',') if x.strip()]
                    langs.update(parts)
            return sorted(langs) if self.sort else list(langs)

        df[self.target_column] = df.apply(_combine_languages, axis=1)
        return df
