from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from jwt import (
    ExpiredSignatureError,
    InvalidTokenError,
)

from sqlalchemy.orm import Session

from app.core.security import (
    criar_token_de_acesso,
    decodificar_token,
    verificar_senha,
)

from app.database.database import (
    obter_sessao,
)

from app.models.user import Usuario

from app.services.user_login.user_repository import (
    buscar_usuario_por_email,
    buscar_usuario_por_id,
)


bearer_scheme = HTTPBearer()


def autenticar_usuario(
    session: Session,
    email: str,
    password: str,
) -> Usuario | None:

    user = buscar_usuario_por_email(
        session=session,
        email=email,
    )


    if user is None:

        return None


    if not user.active:

        return None


    senha_valida = verificar_senha(
        plain_password=password,
        hashed_password=user.password_hash,
    )


    if not senha_valida:

        return None


    return user


def criar_token_do_usuario(
    user: Usuario,
) -> str:

    return criar_token_de_acesso(
        user_id=user.id
    )


def obter_usuario_autenticado(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),

    session: Session = Depends(
        obter_sessao
    ),
) -> Usuario:

    token = credentials.credentials


    try:

        payload = decodificar_token(
            token
        )


        subject = payload.get(
            "sub"
        )


        if subject is None:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido.",
            )


        user_id = int(
            subject
        )


    except ExpiredSignatureError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada.",
        )


    except (
        InvalidTokenError,
        ValueError,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        )


    user = buscar_usuario_por_id(
        session=session,
        user_id=user_id,
    )


    if (
        user is None
        or
        not user.active
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autorizado.",
        )


    return user