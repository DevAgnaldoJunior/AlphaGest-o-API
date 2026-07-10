from getpass import getpass

from app.core.security import (
    gerar_hash_da_senha,
)

from app.database.database import (
    SessionLocal,
)

from app.services.user_login.user_repository import (
    buscar_usuario_por_email,
    criar_usuario,
)


def main() -> None:

    print()
    print("=== Cadastro de usuário ===")
    print()


    nome = input(
        "Nome: "
    ).strip()


    email = input(
        "E-mail: "
    ).strip()


    senha = getpass(
        "Senha: "
    )


    confirmar_senha = getpass(
        "Confirme a senha: "
    )


    if not nome:

        print(
            "O nome é obrigatório."
        )

        return


    if not email:

        print(
            "O e-mail é obrigatório."
        )

        return


    if not senha:

        print(
            "A senha é obrigatória."
        )

        return


    if senha != confirmar_senha:

        print(
            "As senhas não coincidem."
        )

        return


    session = SessionLocal()


    try:

        usuario_existente = (
            buscar_usuario_por_email(
                session=session,
                email=email,
            )
        )


        if usuario_existente is not None:

            print(
                "Já existe um usuário "
                "cadastrado com esse e-mail."
            )

            return


        senha_hash = gerar_hash_da_senha(
            senha
        )


        usuario = criar_usuario(
            session=session,
            name=nome,
            email=email,
            password_hash=senha_hash,
        )


        print()
        print(
            "Usuário criado com sucesso."
        )

        print(
            f"ID: {usuario.id}"
        )

        print(
            f"Nome: {usuario.name}"
        )

        print(
            f"E-mail: {usuario.email}"
        )


    except Exception as erro:

        session.rollback()


        print()
        print(
            "Erro ao criar usuário:"
        )

        print(
            str(erro)
        )


    finally:

        session.close()


if __name__ == "__main__":

    main()