from collections.abc import Generator

from sqlalchemy import (
    create_engine,
    inspect,
    text,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from app.services.date_normalizer import (
    normalizar_data_da_transacao,
)


DATABASE_URL = "sqlite:///./alpha.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def obter_sessao() -> Generator[
    Session,
    None,
    None,
]:

    session = SessionLocal()

    try:

        yield session

    finally:

        session.close()


def adicionar_coluna_data_da_transacao() -> None:

    inspector = inspect(
        engine
    )

    tables = inspector.get_table_names()


    if "transactions" not in tables:

        return


    columns = inspector.get_columns(
        "transactions"
    )


    column_names = {
        column["name"]
        for column in columns
    }


    if (
        "transaction_date"
        in column_names
    ):

        return


    with engine.begin() as connection:

        connection.execute(
            text(
                """
                ALTER TABLE transactions
                ADD COLUMN transaction_date DATE
                """
            )
        )


def adicionar_colunas_de_privacidade() -> None:

    inspector = inspect(
        engine
    )


    tables = inspector.get_table_names()


    if "users" not in tables:

        return


    columns = inspector.get_columns(
        "users"
    )


    column_names = {
        column["name"]
        for column in columns
    }


    with engine.begin() as connection:

        if (
            "privacy_terms_accepted_at"
            not in column_names
        ):

            connection.execute(
                text(
                    """
                    ALTER TABLE users
                    ADD COLUMN privacy_terms_accepted_at DATETIME
                    """
                )
            )


        if (
            "privacy_terms_version"
            not in column_names
        ):

            connection.execute(
                text(
                    """
                    ALTER TABLE users
                    ADD COLUMN privacy_terms_version VARCHAR(20)
                    """
                )
            )


def preencher_datas_antigas() -> None:

    with engine.begin() as connection:

        rows = connection.execute(
            text(
                """
                SELECT
                    t.id,
                    t.date,
                    i.due_date,
                    i.period_start,
                    i.period_end

                FROM transactions t

                LEFT JOIN invoices i
                    ON i.id = t.invoice_id

                WHERE
                    t.transaction_date IS NULL
                    AND t.invoice_id IS NOT NULL
                """
            )
        ).mappings().all()


        for row in rows:

            normalized_date = (
                normalizar_data_da_transacao(
                    date_text=row["date"],
                    due_date=row["due_date"],
                    period_start=row[
                        "period_start"
                    ],
                    period_end=row[
                        "period_end"
                    ],
                )
            )


            if normalized_date is None:

                continue


            connection.execute(
                text(
                    """
                    UPDATE transactions

                    SET transaction_date =
                        :transaction_date

                    WHERE id =
                        :transaction_id
                    """
                ),
                {
                    "transaction_date": (
                        normalized_date.isoformat()
                    ),

                    "transaction_id":
                        row["id"],
                },
            )


def criar_tabelas() -> None:

    Base.metadata.create_all(
        bind=engine
    )


    adicionar_coluna_data_da_transacao()


    adicionar_colunas_de_privacidade()


    preencher_datas_antigas()