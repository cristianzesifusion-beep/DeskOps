"""Interfaccia grafica e funzioni principali di DeskOps."""

import csv
import sys

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import select

from database import Base, SessionLocal, engine
from models import Asset


# Crea le tabelle mancanti senza cambiare quelle già presenti.
Base.metadata.create_all(bind=engine)

# Avvia l'applicazione grafica.
app = QApplication(sys.argv)

# Crea la finestra principale.
window = QMainWindow()
window.setWindowTitle("DeskOps - Gestione asset IT")
window.resize(1000, 700)

# Il layout verticale contiene modulo, ricerca, tabella e pulsanti.
form_widget = QWidget()
main_layout = QVBoxLayout(form_widget)

# Crea il modulo per inserire o modificare un asset.
form = QFormLayout()
main_layout.addLayout(form)

name_input = QLineEdit()
category_input = QLineEdit()
serial_input = QLineEdit()
assigned_to_input = QLineEdit()

# Lo stato si sceglie da un elenco predefinito.
status_input = QComboBox()
status_input.addItems(
    ["In uso", "In magazzino", "In riparazione", "Dismesso"]
)

form.addRow("Nome dispositivo:", name_input)
form.addRow("Categoria:", category_input)
form.addRow("Numero seriale:", serial_input)
form.addRow("Assegnato a:", assigned_to_input)
form.addRow("Stato:", status_input)

# Il pulsante salva un nuovo asset.
save_button = QPushButton("Salva asset")
form.addRow(save_button)

# Il campo ricerca filtra la tabella mentre si scrive.
search_input = QLineEdit()
search_input.setPlaceholderText(
    "Cerca per ID, nome, categoria, seriale, assegnatario o stato..."
)
main_layout.addWidget(search_input)

# La tabella mostra gli asset salvati nel database.
asset_table = QTableWidget()
asset_table.setColumnCount(6)
asset_table.setHorizontalHeaderLabels(
    [
        "ID",
        "Nome",
        "Categoria",
        "Numero seriale",
        "Assegnato a",
        "Stato",
    ]
)
asset_table.setSelectionBehavior(
    QTableWidget.SelectionBehavior.SelectRows
)
main_layout.addWidget(asset_table)

# I pulsanti seguenti agiscono sulla riga selezionata.
delete_button = QPushButton("Elimina asset selezionato")
edit_button = QPushButton("Carica selezionato per modifica")
update_button = QPushButton("Salva modifiche")
export_button = QPushButton("Esporta inventario in CSV")

main_layout.addWidget(delete_button)
main_layout.addWidget(edit_button)
main_layout.addWidget(update_button)
main_layout.addWidget(export_button)

window.setCentralWidget(form_widget)


def filter_assets(search_text: str) -> None:
    """Nasconde le righe che non contengono il testo cercato."""
    text = search_text.casefold().strip()

    for row in range(asset_table.rowCount()):
        row_values = []

        for column in range(asset_table.columnCount()):
            item = asset_table.item(row, column)
            if item is not None:
                row_values.append(item.text())

        row_text = " ".join(row_values).casefold()
        asset_table.setRowHidden(row, text not in row_text)


def refresh_assets() -> None:
    """Ricarica dalla tabella SQLite tutti gli asset."""
    with SessionLocal() as session:
        assets = session.scalars(
            select(Asset).order_by(Asset.id)
        ).all()

    asset_table.setRowCount(len(assets))

    for row, asset in enumerate(assets):
        values = (
            asset.id,
            asset.name,
            asset.category,
            asset.serial_number,
            asset.assigned_to,
            asset.status,
        )

        for column, value in enumerate(values):
            asset_table.setItem(
                row,
                column,
                QTableWidgetItem(str(value)),
            )

    # Mantiene la ricerca attiva anche dopo un aggiornamento.
    filter_assets(search_input.text())
    asset_table.resizeColumnsToContents()


def get_selected_asset_id() -> int | None:
    """Restituisce l'ID della riga selezionata, oppure None."""
    selected_rows = asset_table.selectionModel().selectedRows()

    if not selected_rows:
        return None

    row = selected_rows[0].row()
    id_item = asset_table.item(row, 0)

    if id_item is None:
        return None

    return int(id_item.text())


def save_asset() -> None:
    """Controlla il modulo e inserisce un nuovo asset nel database."""
    name = name_input.text().strip()
    category = category_input.text().strip()

    # Nome e categoria sono obbligatori.
    if not name or not category:
        QMessageBox.warning(
            window,
            "Dati mancanti",
            "Inserisci il nome del dispositivo e la categoria.",
        )
        return

    with SessionLocal() as session:
        asset = Asset(
            name=name,
            category=category,
            serial_number=serial_input.text().strip(),
            assigned_to=assigned_to_input.text().strip(),
            status=status_input.currentText(),
        )
        session.add(asset)
        session.commit()

    # Svuota i campi dopo aver salvato il nuovo asset.
    name_input.clear()
    category_input.clear()
    serial_input.clear()
    assigned_to_input.clear()
    status_input.setCurrentIndex(0)

    refresh_assets()
    QMessageBox.information(
        window,
        "Salvato",
        "Asset aggiunto al database.",
    )


def load_selected_asset() -> None:
    """Carica nel modulo i dati dell'asset selezionato."""
    asset_id = get_selected_asset_id()

    if asset_id is None:
        QMessageBox.warning(
            window,
            "Nessuna selezione",
            "Seleziona prima una riga della tabella.",
        )
        return

    with SessionLocal() as session:
        asset = session.get(Asset, asset_id)

        if asset is None:
            QMessageBox.warning(window, "Errore", "Asset non trovato.")
            refresh_assets()
            return

        # Copia i valori prima di chiudere la sessione del database.
        asset_data = (
            asset.name,
            asset.category,
            asset.serial_number,
            asset.assigned_to,
            asset.status,
        )

    name_input.setText(asset_data[0])
    category_input.setText(asset_data[1])
    serial_input.setText(asset_data[2])
    assigned_to_input.setText(asset_data[3])
    status_input.setCurrentText(asset_data[4])


def update_selected_asset() -> None:
    """Aggiorna nel database l'asset selezionato."""
    asset_id = get_selected_asset_id()

    if asset_id is None:
        QMessageBox.warning(
            window,
            "Nessuna selezione",
            "Seleziona prima una riga della tabella.",
        )
        return

    name = name_input.text().strip()
    category = category_input.text().strip()

    if not name or not category:
        QMessageBox.warning(
            window,
            "Dati mancanti",
            "Nome e categoria sono obbligatori.",
        )
        return

    with SessionLocal() as session:
        asset = session.get(Asset, asset_id)

        if asset is None:
            QMessageBox.warning(window, "Errore", "Asset non trovato.")
            refresh_assets()
            return

        asset.name = name
        asset.category = category
        asset.serial_number = serial_input.text().strip()
        asset.assigned_to = assigned_to_input.text().strip()
        asset.status = status_input.currentText()
        session.commit()

    refresh_assets()
    QMessageBox.information(
        window,
        "Aggiornato",
        "Modifiche salvate.",
    )


def delete_selected_asset() -> None:
    """Chiede conferma e cancella l'asset selezionato."""
    asset_id = get_selected_asset_id()

    if asset_id is None:
        QMessageBox.warning(
            window,
            "Nessuna selezione",
            "Seleziona prima una riga della tabella.",
        )
        return

    answer = QMessageBox.question(
        window,
        "Conferma eliminazione",
        f"Vuoi eliminare l'asset con ID {asset_id}?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )

    if answer != QMessageBox.StandardButton.Yes:
        return

    with SessionLocal() as session:
        asset = session.get(Asset, asset_id)

        if asset is not None:
            session.delete(asset)
            session.commit()

    refresh_assets()


def export_assets() -> None:
    """Esporta tutti gli asset in un file CSV apribile con Excel."""
    file_path, _ = QFileDialog.getSaveFileName(
        window,
        "Esporta inventario",
        "deskops_inventario.csv",
        "File CSV (*.csv)",
    )

    # Se l'utente annulla la finestra, non esporta.
    if not file_path:
        return

    with SessionLocal() as session:
        assets = session.scalars(
            select(Asset).order_by(Asset.id)
        ).all()

    try:
        # utf-8-sig aiuta Excel a riconoscere accenti e caratteri italiani.
        with open(file_path, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                [
                    "ID",
                    "Nome",
                    "Categoria",
                    "Numero seriale",
                    "Assegnato a",
                    "Stato",
                ]
            )

            for asset in assets:
                writer.writerow(
                    [
                        asset.id,
                        asset.name,
                        asset.category,
                        asset.serial_number,
                        asset.assigned_to,
                        asset.status,
                    ]
                )
    except OSError as error:
        QMessageBox.critical(
            window,
            "Errore di esportazione",
            f"Non è stato possibile scrivere il file:\n{error}",
        )
        return

    QMessageBox.information(
        window,
        "Esportazione completata",
        "Inventario esportato correttamente.",
    )


# Collega pulsanti e ricerca alle funzioni.
save_button.clicked.connect(save_asset)
delete_button.clicked.connect(delete_selected_asset)
edit_button.clicked.connect(load_selected_asset)
update_button.clicked.connect(update_selected_asset)
export_button.clicked.connect(export_assets)
search_input.textChanged.connect(filter_assets)

# Mostra gli asset esistenti all'avvio.
refresh_assets()

window.show()
sys.exit(app.exec())
