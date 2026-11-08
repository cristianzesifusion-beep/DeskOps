"""Configurazione del database SQLite locale di DeskOps."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Usa la cartella dati locale di Windows, con un percorso alternativo.
local_app_data = Path(
    os.environ.get(
        "LOCALAPPDATA",
        str(Path.home() / "AppData" / "Local"),
    )
)

# Il database viene tenuto fuori dalla cartella del codice.
data_folder = local_app_data / "DeskOps"
data_folder.mkdir(parents=True, exist_ok=True)
database_file = data_folder / "deskops.db"

# Crea il collegamento a SQLite.
engine = create_engine(f"sqlite:///{database_file.as_posix()}")


class Base(DeclarativeBase):
    """Classe base per i modelli delle tabelle."""


# Crea sessioni con cui leggere e salvare i dati.
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
