import os

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt

from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "troque-esta-chave-em-producao",
)


ALGORITHM = "HS256"


ACCESS_TOKEN_EXPIRE_MINUTES = 480


def gerar_hash_da_senha(
    password: str,
) -> str:

    return password_hash.hash(
        password
    )


def verificar_senha(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def criar_token_de_acesso(
    user_id: int,
) -> str:

    expiration = (
        datetime.now(
            timezone.utc
        )
        +
        timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )


    payload = {
        "sub": str(user_id),
        "exp": expiration,
    }


    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decodificar_token(
    token: str,
) -> dict:

    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )