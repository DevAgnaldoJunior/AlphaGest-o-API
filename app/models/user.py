from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.database import Base


class Usuario(Base):

    __tablename__ = "users"


    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )


    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )


    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )


    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


    privacy_terms_accepted_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


    privacy_terms_version: Mapped[
        str | None
    ] = mapped_column(
        String(20),
        nullable=True,
    )