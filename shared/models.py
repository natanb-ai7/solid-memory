"""ORM models shared between services."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db import Base


class Make(Base):
    __tablename__ = "makes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    models: Mapped[list["Model"]] = relationship(
        "Model", back_populates="make", cascade="all, delete-orphan"
    )


class Model(Base):
    __tablename__ = "models"
    __table_args__ = (UniqueConstraint("make_id", "name", name="uq_model_make_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    make_id: Mapped[int] = mapped_column(ForeignKey("makes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    make: Mapped[Make] = relationship("Make", back_populates="models")
    trims: Mapped[list["Trim"]] = relationship(
        "Trim", back_populates="model", cascade="all, delete-orphan"
    )


class Trim(Base):
    __tablename__ = "trims"
    __table_args__ = (UniqueConstraint("model_id", "name", name="uq_trim_model_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    model: Mapped[Model] = relationship("Model", back_populates="trims")
