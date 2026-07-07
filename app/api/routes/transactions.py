from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.database.database import obter_sessao

from app.schemas.transaction import (
    CadastroCompraManual,
    RespostaFiltroTransacoes,
    RespostaFiltrosTransacoes,
    RespostaTransacao,
    TipoTransacao,
)

from app.services.invoice_repository import (
    buscar_fatura_por_id,
)

from app.services.transaction_repository import (
    cadastrar_compra_manual,
    calcular_total_das_transacoes,
    filtrar_transacoes,
    identificar_origem_da_transacao,
)


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.post(
    "/manual",
    response_model=RespostaTransacao,
    status_code=201,
)
def cadastrar_compra(
    purchase_data: CadastroCompraManual,
    session: Session = Depends(
        obter_sessao
    ),
) -> RespostaTransacao:

    if purchase_data.invoice_id is not None:

        invoice = buscar_fatura_por_id(
            session=session,
            invoice_id=purchase_data.invoice_id,
        )

        if invoice is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Fatura informada não encontrada."
                ),
            )

    try:

        transaction = cadastrar_compra_manual(
            session=session,
            purchase_data=purchase_data,
            invoice_id=purchase_data.invoice_id,
        )

    except Exception as error:

        session.rollback()

        print(
            f"Erro ao cadastrar compra: {error}"
        )

        raise HTTPException(
            status_code=422,
            detail=(
                "Não foi possível cadastrar "
                "a compra manual."
            ),
        )

    origin = identificar_origem_da_transacao(
        transaction
    )

    return RespostaTransacao(
        id=transaction.id,
        invoice_id=transaction.invoice_id,
        date=transaction.date,
        card=transaction.card,
        description=transaction.description,
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category,
        origin=origin,
        page=transaction.page,
    )


@router.get(
    "/filter",
    response_model=RespostaFiltroTransacoes,
)
def consultar_transacoes_com_filtros(
    invoice_id: int | None = Query(
        default=None,
        description="ID da fatura",
    ),

    card: str | None = Query(
        default=None,
        description="Final do cartão",
    ),

    date_text: str | None = Query(
        default=None,
        alias="date",
        description="Data textual. Exemplo: 05 JUN",
    ),

    month: str | None = Query(
        default=None,
        description="Mês abreviado. Exemplo: JUN",
    ),

    category: str | None = Query(
        default=None,
        description="Categoria",
    ),

    type: TipoTransacao | None = Query(
        default=None,
        description="Tipo da transação",
    ),

    start_date: date | None = Query(
        default=None,
        description=(
            "Data inicial. "
            "Formato: 2026-06-01"
        ),
    ),

    end_date: date | None = Query(
        default=None,
        description=(
            "Data final. "
            "Formato: 2026-06-30"
        ),
    ),

    session: Session = Depends(
        obter_sessao
    ),

) -> RespostaFiltroTransacoes:

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "A data inicial não pode ser "
                "posterior à data final."
            ),
        )

    transactions = filtrar_transacoes(
        session=session,
        invoice_id=invoice_id,
        card=card,
        date_text=date_text,
        month=month,
        category=category,
        transaction_type=type,
        start_date=start_date,
        end_date=end_date,
    )

    total_amount = calcular_total_das_transacoes(
        transactions
    )

    response_transactions = [
        RespostaTransacao(
            id=transaction.id,
            invoice_id=transaction.invoice_id,
            date=transaction.date,
            card=transaction.card,
            description=transaction.description,
            amount=transaction.amount,
            type=transaction.type,
            category=transaction.category,
            origin=(
                identificar_origem_da_transacao(
                    transaction
                )
            ),
            page=transaction.page,
        )
        for transaction in transactions
    ]

    return RespostaFiltroTransacoes(

        filters=RespostaFiltrosTransacoes(
            invoice_id=invoice_id,
            card=card,
            date=date_text,
            month=month,
            category=category,
            type=type,
            start_date=start_date,
            end_date=end_date,
        ),

        total_transactions=len(
            response_transactions
        ),

        total_amount=total_amount,

        transactions=response_transactions,
    )