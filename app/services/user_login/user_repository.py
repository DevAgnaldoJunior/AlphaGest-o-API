from datetime import datetime

from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.user import Usuario


def buscar_usuario_por_email(
    session: Session,
    email: str,
) -> Usuario | None:

    normalized_email = (
        email
        .lower()
        .strip()
    )


    statement = (
        select(Usuario)
        .where(
            Usuario.email
            ==
            normalized_email
        )
    )


    return session.scalar(
        statement
    )


def buscar_usuario_por_id(
    session: Session,
    user_id: int,
) -> Usuario | None:

    statement = (
        select(Usuario)
        .where(
            Usuario.id == user_id
        )
    )


    return session.scalar(
        statement
    )


def criar_usuario(
    session: Session,
    name: str,
    email: str,
    password_hash: str,
    privacy_terms_accepted_at:
        datetime | None = None,
    privacy_terms_version:
        str | None = None,
) -> Usuario:

    usuario = Usuario(
        name=name.strip(),

        email=(
            email
            .lower()
            .strip()
        ),

        password_hash=password_hash,

        active=True,

        privacy_terms_accepted_at=(
            privacy_terms_accepted_at
        ),

        privacy_terms_version=(
            privacy_terms_version
        ),
    )


    session.add(
        usuario
    )


    session.commit()


    session.refresh(
        usuario
    )


    return usuario