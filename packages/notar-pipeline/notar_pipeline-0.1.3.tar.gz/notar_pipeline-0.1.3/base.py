from abc import ABC, abstractmethod
import logging
from typing import Tuple
import pandas as pd


class BaseParser(ABC):
    """Parse raw record -> normalized dict (no pandas)."""

    @abstractmethod
    def parse(self, raw: dict) -> dict:
        raise NotImplementedError

    def safe_parse(self, raw: dict) -> dict | None:
        """
        Wraps parse() with try/except and logs errors.
        """
        logger = logging.getLogger(self.__class__.__name__)

        try:
            return self.parse(raw)
        except Exception as e:
            logger.error(f"Error while parsing record: {e}", exc_info=True)
            return None
        


class BaseTransformer(ABC):
    """Transform DataFrame -> DataFrame (pure functions)."""
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
    
    def safe_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Runs transform() safely with logging."""
        logger = logging.getLogger(self.__class__.__name__)
        try:
            return self.transform(df)
        except Exception as e:
            logger.error(f"Transformation failed in {self.__class__.__name__}: {e}", exc_info=True)
            return df.copy()





class BaseExtractor(ABC):
    """Abstract base class for all data extractors."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def extract(self, source_path: str):
        """Extract data from a given source and return it."""
        pass
