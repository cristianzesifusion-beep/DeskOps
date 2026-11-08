"""Modelli SQLAlchemy usati da DeskOps."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Asset(Base):
    """Rappresenta un dispositivo registrato in DeskOps."""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(120), default="")
    assigned_to: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(40), default="In uso")
