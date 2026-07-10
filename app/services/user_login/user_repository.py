from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.user import Usuario


def buscar_usuario_por_email(
    session: Session,
    email: str,
) -> Usuario | None:

    statement = (
        select(Usuario)
        .where(
            Usuario.email
            ==
            email.lower().strip()
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
) -> Usuario:

    usuario = Usuario(
        name=name.strip(),

        email=email
        .lower()
        .strip(),

        password_hash=password_hash,

        active=True,
    )


    session.add(
        usuario
    )


    session.commit()


    session.refresh(
        usuario
    )


    return usuario