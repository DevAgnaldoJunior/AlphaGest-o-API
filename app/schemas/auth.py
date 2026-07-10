from pydantic import (
    BaseModel,
    EmailStr,
)


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class UsuarioResposta(BaseModel):

    id: int

    name: str

    email: str


class LoginResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    user: UsuarioResposta