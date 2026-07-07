from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


if TYPE_CHECKING:
    from app.models.transaction import Transacao


class Fatura(Base):

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    total_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    due_date: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    period_start: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    period_end: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    transactions: Mapped[list[Transacao]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
    )