from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fatura import Fatura
from app.models.transaction import Transacao

from app.services.invoice_parser import (
    MetadadosFatura,
    TransacaoAnalisada,
)


def salvar_fatura(
    session: Session,
    filename: str,
    metadata: MetadadosFatura,
    transactions: list[TransacaoAnalisada],
) -> Fatura:

    invoice = Fatura(
        filename=filename,
        total_amount=metadata.total_amount,
        due_date=metadata.due_date,
        period_start=metadata.period_start,
        period_end=metadata.period_end,
    )

    for transaction in transactions:

        database_transaction = Transacao(
            date=transaction.date,
            card=transaction.card,
            description=transaction.description,
            amount=transaction.amount,
            type=transaction.type,
            category=transaction.category,
            page=transaction.page,
        )

        invoice.transactions.append(
            database_transaction
        )

    session.add(invoice)

    session.commit()

    session.refresh(invoice)

    return invoice


def listar_faturas(
    session: Session,
) -> list[Fatura]:

    statement = (
        select(Fatura)
        .order_by(Fatura.id.desc())
    )

    result = session.scalars(
        statement
    )

    return list(
        result.all()
    )