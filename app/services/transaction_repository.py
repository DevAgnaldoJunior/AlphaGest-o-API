from datetime import date

from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import Session

from app.models.transaction import Transacao

from app.schemas.transaction import (
    AtualizacaoTransacao,
    CadastroCompraManual,
)

from app.services.date_normalizer import (
    formatar_data_para_texto,
)


def buscar_transacao_por_id(
    session: Session,
    invoice_id: int,
    transaction_id: int,
) -> Transacao | None:

    statement = (
        select(Transacao)
        .where(
            Transacao.id == transaction_id,
            Transacao.invoice_id == invoice_id,
        )
    )

    transaction = session.scalar(
        statement
    )

    return transaction


def buscar_transacao_global_por_id(
    session: Session,
    transaction_id: int,
) -> Transacao | None:

    statement = (
        select(Transacao)
        .where(
            Transacao.id == transaction_id
        )
    )

    transaction = session.scalar(
        statement
    )

    return transaction


def cadastrar_compra_manual(
    session: Session,
    purchase_data: CadastroCompraManual,
    invoice_id: int | None = None,
) -> Transacao:

    date_text = formatar_data_para_texto(
        purchase_data.transaction_date
    )

    transaction = Transacao(
        invoice_id=invoice_id,

        date=date_text,

        transaction_date=(
            purchase_data.transaction_date
        ),

        card=purchase_data.card,

        description=(
            purchase_data
            .description
            .strip()
        ),

        amount=purchase_data.amount,

        type="compra",

        category=(
            purchase_data
            .category
            .strip()
        ),

        page=0,
    )

    session.add(
        transaction
    )

    session.commit()

    session.refresh(
        transaction
    )

    return transaction


def atualizar_transacao(
    session: Session,
    transaction: Transacao,
    update_data: AtualizacaoTransacao,
) -> Transacao:

    changes = update_data.model_dump(
        exclude_unset=True
    )

    if "transaction_date" in changes:

        new_date = changes.pop(
            "transaction_date"
        )

        if new_date is not None:

            transaction.transaction_date = (
                new_date
            )

            transaction.date = (
                formatar_data_para_texto(
                    new_date
                )
            )

    for field, value in changes.items():

        setattr(
            transaction,
            field,
            value,
        )

    session.commit()

    session.refresh(
        transaction
    )

    return transaction


def excluir_transacao(
    session: Session,
    transaction: Transacao,
) -> None:

    session.delete(
        transaction
    )

    session.commit()


def filtrar_transacoes(
    session: Session,
    invoice_id: int | None = None,
    card: str | None = None,
    date_text: str | None = None,
    month: str | None = None,
    category: str | None = None,
    transaction_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Transacao]:

    statement = select(
        Transacao
    )

    if invoice_id is not None:

        statement = statement.where(
            Transacao.invoice_id == invoice_id
        )

    if card:

        statement = statement.where(
            Transacao.card == card
        )

    if date_text:

        statement = statement.where(
            func.upper(
                Transacao.date
            )
            ==
            date_text.upper()
        )

    if month:

        statement = statement.where(
            func.upper(
                Transacao.date
            ).like(
                f"%{month.upper()}%"
            )
        )

    if category:

        statement = statement.where(
            func.lower(
                Transacao.category
            )
            ==
            category.lower()
        )

    if transaction_type:

        statement = statement.where(
            Transacao.type
            ==
            transaction_type
        )

    if start_date is not None:

        statement = statement.where(
            Transacao.transaction_date
            >=
            start_date
        )

    if end_date is not None:

        statement = statement.where(
            Transacao.transaction_date
            <=
            end_date
        )

    statement = statement.order_by(
        Transacao.transaction_date.asc(),
        Transacao.id.asc(),
    )

    result = session.scalars(
        statement
    )

    return list(
        result.all()
    )


def calcular_total_das_transacoes(
    transactions: list[Transacao],
) -> float:

    total = 0.0

    for transaction in transactions:

        if transaction.type in (
            "compra",
            "financiamento",
        ):

            total += abs(
                transaction.amount
            )

            continue


        if transaction.type == "estorno":

            total -= abs(
                transaction.amount
            )


    return round(
        total,
        2,
    )
def identificar_origem_da_transacao(
    transaction: Transacao,
) -> str:

    if transaction.invoice_id is None:

        return "lancamento_avulso"

    return "fatura"

def listar_opcoes_dos_filtros(
    session: Session,
) -> dict:

    cards_statement = (
        select(
            Transacao.card
        )
        .where(
            Transacao.card.is_not(None),
            Transacao.card != "",
        )
        .distinct()
        .order_by(
            Transacao.card.asc()
        )
    )


    categories_statement = (
        select(
            Transacao.category
        )
        .where(
            Transacao.category.is_not(None),
            Transacao.category != "",
        )
        .distinct()
        .order_by(
            Transacao.category.asc()
        )
    )


    types_statement = (
        select(
            Transacao.type
        )
        .where(
            Transacao.type.is_not(None),
            Transacao.type != "",
        )
        .distinct()
        .order_by(
            Transacao.type.asc()
        )
    )


    dates_statement = select(
        func.min(
            Transacao.transaction_date
        ),
        func.max(
            Transacao.transaction_date
        ),
    )


    cards = list(
        session.scalars(
            cards_statement
        ).all()
    )


    categories = list(
        session.scalars(
            categories_statement
        ).all()
    )


    types = list(
        session.scalars(
            types_statement
        ).all()
    )


    min_date, max_date = session.execute(
        dates_statement
    ).one()


    return {
        "cards": cards,
        "categories": categories,
        "types": types,
        "min_date": min_date,
        "max_date": max_date,
    }