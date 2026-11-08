"""Aggiunge in modo sicuro i campi recenti ai database DeskOps esistenti."""

from database import Base, engine
from models import Asset  # Registra il modello prima di creare la tabella.


# Su un database nuovo crea già la tabella con tutte le colonne attuali.
Base.metadata.create_all(bind=engine)

with engine.begin() as connection:
    # Legge le colonne esistenti per non aggiungerle due volte.
    columns = {
        row[1]
        for row in connection.exec_driver_sql("PRAGMA table_info(assets)")
    }

    if "assigned_to" not in columns:
        connection.exec_driver_sql(
            "ALTER TABLE assets "
            "ADD COLUMN assigned_to VARCHAR(120) NOT NULL DEFAULT ''"
        )

    if "status" not in columns:
        connection.exec_driver_sql(
            "ALTER TABLE assets "
            "ADD COLUMN status VARCHAR(40) NOT NULL DEFAULT 'In uso'"
        )

print("Aggiornamento del database completato.")
