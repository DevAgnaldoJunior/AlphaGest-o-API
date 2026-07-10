from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.database import (
    obter_sessao,
)

from app.models.user import Usuario

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UsuarioResposta,
)

from app.services.user_login.auth_service import (
    autenticar_usuario,
    criar_token_do_usuario,
    obter_usuario_autenticado,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    login_data: LoginRequest,

    session: Session = Depends(
        obter_sessao
    ),
) -> LoginResponse:

    user = autenticar_usuario(
        session=session,
        email=login_data.email,
        password=login_data.password,
    )


    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )


    access_token = criar_token_do_usuario(
        user
    )


    return LoginResponse(
        access_token=access_token,

        token_type="bearer",

        user=UsuarioResposta(
            id=user.id,
            name=user.name,
            email=user.email,
        ),
    )


@router.get(
    "/me",
    response_model=UsuarioResposta,
)
def consultar_usuario_autenticado(
    user: Usuario = Depends(
        obter_usuario_autenticado
    ),
) -> UsuarioResposta:

    return UsuarioResposta(
        id=user.id,
        name=user.name,
        email=user.email,
    )