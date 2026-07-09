from pydantic import BaseModel

from app.schemas.transaction import RespostaTransacao


class RespostaExtracaoFatura(BaseModel):
    filename: str
    content_type: str
    size: int
    pages: int
    text: str


class RespostaLinhaPdf(BaseModel):
    page: int
    y: float
    text: str


class RespostaLinhasFatura(BaseModel):
    filename: str
    lines: list[RespostaLinhaPdf]


class RespostaMetadadosFatura(BaseModel):
    total_amount: float | None
    due_date: str | None
    period_start: str | None
    period_end: str | None


class RespostaResumoTransacoes(BaseModel):
    compra: int
    estorno: int
    pagamento: int
    financiamento: int


class RespostaResumoCategoria(BaseModel):
    category: str
    total_transactions: int
    total_amount: float


class RespostaTransacoesFatura(BaseModel):
    filename: str
    invoice: RespostaMetadadosFatura
    summary: RespostaResumoTransacoes
    category_summary: list[RespostaResumoCategoria]
    total_transactions: int
    transactions: list[RespostaTransacao]


class RespostaFaturaSalva(BaseModel):
    id: int
    filename: str
    total_amount: float | None
    due_date: str | None
    total_transactions: int


class RespostaFaturaLista(BaseModel):
    id: int
    filename: str
    total_amount: float | None
    due_date: str | None
    period_start: str | None
    period_end: str | None
    total_transactions: int


class RespostaDetalheFatura(BaseModel):
    id: int
    filename: str
    invoice: RespostaMetadadosFatura
    summary: RespostaResumoTransacoes
    category_summary: list[RespostaResumoCategoria]
    total_transactions: int
    transactions: list[RespostaTransacao]

    
class RespostaExclusaoFatura(BaseModel):
    message: str
    invoice_id: int
    deleted_transactions: int