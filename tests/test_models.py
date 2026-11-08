"""Controlli di base sul modello Asset."""

from models import Asset


def test_asset_uses_assets_table():
    assert Asset.__tablename__ == "assets"


def test_asset_has_inventory_fields():
    expected_fields = {
        "id",
        "name",
        "category",
        "serial_number",
        "assigned_to",
        "status",
    }

    assert expected_fields.issubset(Asset.__table__.columns.keys())
