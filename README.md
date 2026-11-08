# DeskOps

DeskOps è un'applicazione desktop locale per registrare e gestire asset IT su Windows. Usa PySide6 per l'interfaccia e SQLite tramite SQLAlchemy per conservare i dati nel profilo utente.

## Funzioni

- Inserimento, visualizzazione, modifica ed eliminazione degli asset
- Ricerca per ID, nome, categoria, seriale, assegnatario e stato
- Esportazione dell'inventario in CSV, compatibile con Excel
- Database locale in `%LOCALAPPDATA%\DeskOps\deskops.db`

## Avvio su Windows con PowerShell

Dalla cartella `DeskOps`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Per installare anche pytest:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Per aggiornare un vecchio database che non contiene ancora i campi `assigned_to` e `status`:

```powershell
.\.venv\Scripts\python.exe migrate_db.py
```

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## File principali

- `main.py`: interfaccia e funzioni dell'applicazione
- `database.py`: percorso locale, collegamento SQLite e sessioni
- `models.py`: modello SQLAlchemy dell'asset
- `migrate_db.py`: migrazione compatibile con database precedenti
- `tests/`: test del modello
