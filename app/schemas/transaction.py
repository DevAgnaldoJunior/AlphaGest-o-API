from datetime import date as Date
from typing import Literal


from pydantic import (
    BaseModel,
    Field,
)


TipoTransacao = Literal[
    "compra",
    "estorno",
    "pagamento",
    "financiamento",
]


OrigemTransacao = Literal[
    "fatura",
    "lancamento_avulso",
]


class RespostaTransacao(BaseModel):
    id: int | None = None

    invoice_id: int | None = None

    date: str

    transaction_date: Date | None = None

    card: str | None

    description: str

    amount: float

    type: TipoTransacao

    category: str

    origin: str

    page: int


class CadastroCompraManual(BaseModel):
    invoice_id: int | None = None

    transaction_date: Date

    card: str = Field(
        min_length=4,
        max_length=4,
        pattern=r"^\d{4}$",
    )

    description: str = Field(
        min_length=2,
        max_length=500,
    )

    amount: float = Field(
        gt=0,
    )

    category: str = Field(
        min_length=2,
        max_length=100,
    )


class AtualizacaoTransacao(BaseModel):
    transaction_date: Date | None = None

    card: str | None = None

    description: str | None = None

    amount: float | None = None

    type: TipoTransacao | None = None

    category: str | None = None


class RespostaExclusaoTransacao(BaseModel):
    message: str

    transaction_id: int


class RespostaFiltrosTransacoes(BaseModel):
    invoice_id: int | None

    card: str | None

    date: str | None

    month: str | None

    category: str | None

    type: TipoTransacao | None

    start_date: Date | None

    end_date: Date | None


class RespostaFiltroTransacoes(BaseModel):
    filters: RespostaFiltrosTransacoes

    total_transactions: int

    total_amount: float

    transactions: list[RespostaTransacao]