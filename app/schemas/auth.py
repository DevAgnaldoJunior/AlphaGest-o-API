from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class CadastroUsuarioRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=120,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    password_confirmation: str = Field(
        min_length=8,
        max_length=128,
    )

    privacy_acceptance: bool


class UsuarioResposta(BaseModel):

    id: int

    name: str

    email: str


class CadastroUsuarioResponse(BaseModel):

    id: int

    name: str

    email: str

    message: str


class LoginResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    user: UsuarioResposta