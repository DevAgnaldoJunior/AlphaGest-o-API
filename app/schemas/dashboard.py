from datetime import date as Date

from pydantic import BaseModel


class RespostaFiltrosDashboard(BaseModel):
    invoice_id: int | None

    card: str | None

    category: str | None

    start_date: Date | None

    end_date: Date | None


class RespostaMaiorCompra(BaseModel):
    transaction_id: int

    description: str

    amount: float

    category: str

    date: Date | None


class RespostaVisaoGeral(BaseModel):
    total_spent: float

    net_spent: float

    total_purchases: int

    average_ticket: float

    largest_purchase: RespostaMaiorCompra | None


class RespostaDistribuicaoCategoria(BaseModel):
    category: str

    total_amount: float

    percentage: float

    total_transactions: int


class RespostaDistribuicaoCartao(BaseModel):
    card: str

    total_amount: float

    percentage: float

    total_transactions: int


class RespostaEstabelecimento(BaseModel):
    merchant: str

    total_transactions: int

    total_amount: float

    average_ticket: float


class RespostaPequenasCompras(BaseModel):
    threshold: float

    total_transactions: int

    total_amount: float

    percentage_of_spending: float

    percentage_of_transactions: float


class RespostaEstornos(BaseModel):
    total_transactions: int

    total_amount: float


class RespostaFinanciamentos(BaseModel):
    total_transactions: int

    total_amount: float


class RespostaComprasSemCartao(BaseModel):
    total_transactions: int

    total_amount: float

    percentage_of_spending: float


class RespostaComportamento(BaseModel):
    small_purchases: RespostaPequenasCompras

    refunds: RespostaEstornos

    financing: RespostaFinanciamentos

    purchases_without_card: RespostaComprasSemCartao


class RespostaInsight(BaseModel):
    type: str

    severity: str

    title: str

    message: str

    metric_value: float | None = None


class RespostaDashboard(BaseModel):
    filters: RespostaFiltrosDashboard

    overview: RespostaVisaoGeral

    category_distribution: list[
        RespostaDistribuicaoCategoria
    ]

    card_distribution: list[
        RespostaDistribuicaoCartao
    ]

    merchant_ranking: list[
        RespostaEstabelecimento
    ]

    behavior: RespostaComportamento

    featured_insights: list[
        RespostaInsight
    ]

    additional_insights: list[
        RespostaInsight
    ]