import pandas as pd
from base import BaseTransformer


class GeoTransformer(BaseTransformer):
    """Kombiniert Latitude und Longitude in eine GEO-Spalte im Format (longitude, latitude)."""

    def __init__(self, latitude_col="latitude", longitude_col="longitude", target_column="GEO"):

        self.latitude_col = latitude_col
        self.longitude_col = longitude_col
        self.target_column = target_column

    def transform(self, df):
        df = df.copy()

        def _combine_geo(row):
            lat = row.get(self.latitude_col)
            lon = row.get(self.longitude_col)
            if pd.notna(lat) and pd.notna(lon):
                return (lon, lat)  #(longitude, latitude)
            return None

        df[self.target_column] = df.apply(_combine_geo, axis=1)
        return df
