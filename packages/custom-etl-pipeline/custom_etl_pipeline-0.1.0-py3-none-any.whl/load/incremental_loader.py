import pandas as pd
from datetime import datetime
from ETL.DB.connection import get_connection
from ETL.config.logging_conf import get_logger

logger = get_logger(__name__)

class IncrementalLoader:
    """ inkrementeller Loader mit Upsert-Logik."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def load_incremental(self, table: str, key_cols: list[str]):
        conn = get_connection(self.db_path)

        try:
            logger.info(f"🚀 Starte inkrementelles Laden für '{table}'")

            df_staging = pd.read_sql(f"SELECT * FROM {table}_staging", conn)
            if df_staging.empty:
                logger.info(f"⚠️ {table}_staging leer – übersprungen.")
                return

            # Prüfen, ob Core-Tabelle existiert
            table_exists = pd.read_sql(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'", conn
            )

            if table_exists.empty:
                # Core-Tabelle existiert nicht → direkt anlegen
                df_staging["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df_staging.to_sql(table, conn, if_exists="replace", index=False)
                logger.info(f"🆕 Tabelle '{table}' neu erstellt mit {len(df_staging)} Datensätzen.")
                return

            # Core laden
            df_core = pd.read_sql(f"SELECT * FROM {table}", conn)

            # Fehlende Spalten synchronisieren
            missing_cols = [c for c in df_staging.columns if c not in df_core.columns]
            if missing_cols:
                logger.warning(f"⚠️ Fehlende Spalten in {table}: {missing_cols} — werden ignoriert.")
                df_staging = df_staging.drop(columns=missing_cols)

            # Vergleich nach Hash
            merged = df_staging.merge(
                df_core[key_cols + ["record_hash"]],
                on=key_cols,
                how="left",
                suffixes=("", "_core")
            )
            df_upsert = merged[
                merged["record_hash_core"].isna() | 
                (merged["record_hash"] != merged["record_hash_core"])
            ].drop(columns=["record_hash_core"], errors="ignore")

            if df_upsert.empty:
                logger.info("✅ Keine Änderungen erkannt.")
                return

            df_upsert["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # UPSERT ausführen
            cols = ", ".join(df_upsert.columns)
            placeholders = ", ".join(["?"] * len(df_upsert.columns))
            update_clause = ", ".join(
                f"{c}=excluded.{c}" for c in df_upsert.columns if c not in key_cols
            )
            sql = f"""
                INSERT INTO {table} ({cols})
                VALUES ({placeholders})
                ON CONFLICT({', '.join(key_cols)}) DO UPDATE SET {update_clause};
            """

            conn.executemany(sql, df_upsert.itertuples(index=False, name=None))
            conn.commit()

            logger.info(f"✅ {len(df_upsert)} Datensätze upserted in {table}.")

        except Exception as e:
            logger.exception(f"❌ Fehler beim Laden in '{table}': {e}")

        finally:
            conn.close()
            logger.info("🔒 Verbindung geschlossen.")
