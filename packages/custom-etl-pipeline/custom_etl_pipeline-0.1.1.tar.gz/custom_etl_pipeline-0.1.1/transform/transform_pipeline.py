import json
import logging
import pandas as pd
from typing import Dict, Any
from ETL.base import BaseTransformer

# Importiere alle Transformer
from ETL.transform.cleaning import CleaningTransformer
from ETL.transform.date_transformer import DateNormalizer
from ETL.transform.address_normalizer import AddressNormalizer
from ETL.transform.phone_normalizer import PhoneNormalizer
from ETL.transform.gender_parsing_trasnformer import TitleGenderTransformer
from ETL.transform.url_transformer import URLNormalizer
from ETL.transform.id_generator import IDGenerator
from ETL.transform.hash_generator import HashGenerator


class TransformPipeline:
    """Einfache JSON-gesteuerte Pipeline mit globalen und tabellenspezifischen Transformern."""

    def __init__(self, config_path: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        with open(config_path, "r", encoding="utf-8") as f:
            self.config: Dict[str, Any] = json.load(f)

        # alle bekannten Transformer
        self.registry: Dict[str, BaseTransformer] = {
            "CleaningTransformer": CleaningTransformer(),
            "DateNormalizer": DateNormalizer(),
            "AddressNormalizer": AddressNormalizer(),
            "PhoneNormalizer": PhoneNormalizer(),
            "TitleGenderTransformer": TitleGenderTransformer(),
            "URLNormalizer": URLNormalizer(),
            "IDGenerator": IDGenerator(),
        }

    def transform(self, table_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Führt globale + tabellenspezifische Transformationen aus."""
        self.logger.info(f"Transforming table '{table_name}'")

        # globale Transformer
        for entry in self.config.get("global_transformers", []):
            df = self._apply(entry, df)

        # tabellenspezifische Transformer
        for entry in self.config.get("tables", {}).get(table_name, {}).get("transformers", []):
            df = self._apply(entry, df)

        self.logger.info(f"Finished '{table_name}'")
        return df

    def _apply(self, entry: Dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
        """Führt einen Transformer aus – HashGenerator bekommt dynamische Spalten."""
        name = entry["name"]
        cols = entry.get("columns")

        transformer = HashGenerator(cols) if name == "HashGenerator" else self.registry.get(name)
        if not transformer:
            self.logger.warning(f"Unknown transformer '{name}' – skipped.")
            return df

        self.logger.debug(f"Applying {name} (columns={cols or 'ALL'})")
        return transformer.safe_transform(df)
