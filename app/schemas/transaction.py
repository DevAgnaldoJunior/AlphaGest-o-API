from typing import Literal

from pydantic import BaseModel


TipoTransacao = Literal[
    "compra",
    "estorno",
    "pagamento",
    "financiamento",
]


class RespostaTransacao(BaseModel):
    date: str
    card: str | None
    description: str
    amount: float
    type: TipoTransacao
    category: str
    page: int