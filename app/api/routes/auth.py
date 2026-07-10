from datetime import (
    datetime,
    timezone,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.core.security import (
    gerar_hash_da_senha,
)

from app.database.database import (
    obter_sessao,
)

from app.models.user import Usuario

from app.schemas.auth import (
    CadastroUsuarioRequest,
    CadastroUsuarioResponse,
    LoginRequest,
    LoginResponse,
    UsuarioResposta,
)

from app.services.user_login.auth_service import (
    autenticar_usuario,
    criar_token_do_usuario,
    obter_usuario_autenticado,
)

from app.services.user_login.user_repository import (
    buscar_usuario_por_email,
    criar_usuario,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


VERSAO_TERMOS_PRIVACIDADE = "1.0"


@router.post(
    "/register",
    response_model=CadastroUsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_usuario(
    cadastro: CadastroUsuarioRequest,

    session: Session = Depends(
        obter_sessao
    ),
) -> CadastroUsuarioResponse:

    if not cadastro.privacy_acceptance:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,

            detail=(
                "É necessário aceitar os Termos de Uso "
                "e declarar ciência do Aviso de Privacidade."
            ),
        )


    if (
        cadastro.password
        !=
        cadastro.password_confirmation
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,

            detail=(
                "As senhas informadas não coincidem."
            ),
        )


    usuario_existente = (
        buscar_usuario_por_email(
            session=session,
            email=cadastro.email,
        )
    )


    if usuario_existente is not None:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,

            detail=(
                "Já existe um usuário cadastrado "
                "com este e-mail."
            ),
        )


    senha_hash = gerar_hash_da_senha(
        cadastro.password
    )


    try:

        usuario = criar_usuario(
            session=session,

            name=cadastro.name,

            email=cadastro.email,

            password_hash=senha_hash,

            privacy_terms_accepted_at=(
                datetime.now(
                    timezone.utc
                )
            ),

            privacy_terms_version=(
                VERSAO_TERMOS_PRIVACIDADE
            ),
        )


    except Exception as error:

        session.rollback()


        print(
            f"Erro ao cadastrar usuário: "
            f"{error}"
        )


        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,

            detail=(
                "Não foi possível cadastrar o usuário."
            ),
        )


    return CadastroUsuarioResponse(
        id=usuario.id,

        name=usuario.name,

        email=usuario.email,

        message=(
            "Usuário criado com sucesso."
        ),
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

            detail=(
                "E-mail ou senha inválidos."
            ),
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