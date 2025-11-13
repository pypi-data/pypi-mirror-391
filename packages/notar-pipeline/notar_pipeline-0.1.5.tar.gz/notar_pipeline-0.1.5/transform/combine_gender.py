import pandas as pd
from base import BaseTransformer
from transform.gender_parsing_trasnformer import TitleGenderTransformer

class CombinedGenderTransformer(BaseTransformer):
    """
    Combines title-based gender extraction and gender propagation.
    """

    def __init__(self):
        self.title_transformer = TitleGenderTransformer()

    def transform(self, notar_df: pd.DataFrame, person_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        # Step 1: Extract gender in notar_df
        notar_df = self.title_transformer.transform(notar_df)

        # Step 2: Attach gender to person_df
        merged_person_df = person_df.merge(
            notar_df[["personId", "Gender"]],
            on="personId",
            how="left"
        )

        return notar_df, merged_person_df
