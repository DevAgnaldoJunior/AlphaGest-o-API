import re
from dataclasses import dataclass

from app.services.pdf_extractor import LinhaDocumento
from app.services.transaction_classifier import categorizar_transacao


@dataclass
class TransacaoAnalisada:
    date: str
    card: str | None
    description: str
    amount: float
    type: str
    category: str
    page: int


@dataclass
class MetadadosFatura:
    total_amount: float | None
    due_date: str | None
    period_start: str | None
    period_end: str | None


DATE_PATTERN = r"(?P<date>\d{2}\s+[A-Z]{3})"

CARD_PATTERN = r"(?:••••\s+(?P<card>\d{4})\s+)?"

DESCRIPTION_PATTERN = r"(?P<description>.+?)"

AMOUNT_PATTERN = (
    r"(?P<amount>"
    r"(?:−|-)?R\$\s*"
    r"\d{1,3}(?:\.\d{3})*,\d{2}"
    r")"
)


TRANSACTION_PATTERN = re.compile(
    rf"^{DATE_PATTERN}\s+"
    rf"{CARD_PATTERN}"
    rf"{DESCRIPTION_PATTERN}\s+"
    rf"{AMOUNT_PATTERN}$"
)


def converter_valor_brasileiro(
    value: str,
) -> float:

    normalized = (
        value
        .replace("R$", "")
        .replace(" ", "")
        .replace(".", "")
        .replace(",", ".")
        .replace("−", "-")
    )

    return float(normalized)


def identificar_tipo_da_transacao(
    description: str,
    amount: float,
    section: str,
) -> str:

    normalized_description = (
        description
        .strip()
        .lower()
    )

    if "pagamento" in normalized_description:
        return "pagamento"

    if "estorno" in normalized_description:
        return "estorno"

    if section == "pagamentos_financiamentos":
        return "financiamento"

    if amount < 0:
        return "estorno"

    return "compra"


def analisar_linha_de_transacao(
    line: LinhaDocumento,
    section: str,
) -> TransacaoAnalisada | None:

    match = TRANSACTION_PATTERN.match(
        line.text.strip()
    )

    if not match:
        return None

    date = match.group("date")

    card = match.group("card")

    description = match.group(
        "description"
    ).strip()

    amount = converter_valor_brasileiro(
        match.group("amount")
    )

    transaction_type = identificar_tipo_da_transacao(
        description=description,
        amount=amount,
        section=section,
    )

    category = categorizar_transacao(
        description=description,
        transaction_type=transaction_type,
    )

    return TransacaoAnalisada(
        date=date,
        card=card,
        description=description,
        amount=amount,
        type=transaction_type,
        category=category,
        page=line.page,
    )


def analisar_transacoes(
    lines: list[LinhaDocumento],
) -> list[TransacaoAnalisada]:

    transactions: list[TransacaoAnalisada] = []

    current_section = "transacoes"

    for line in lines:
        normalized_text = (
            line.text
            .strip()
            .lower()
        )

        if "pagamentos e financiamentos" in normalized_text:
            current_section = "pagamentos_financiamentos"
            continue

        transaction = analisar_linha_de_transacao(
            line=line,
            section=current_section,
        )

        if transaction is None:
            continue

        transactions.append(transaction)

    return transactions


def extrair_metadados_da_fatura(
    lines: list[LinhaDocumento],
) -> MetadadosFatura:

    total_amount: float | None = None
    due_date: str | None = None
    period_start: str | None = None
    period_end: str | None = None

    full_text = "\n".join(
        line.text
        for line in lines
    )

    total_match = re.search(
        r"fatura de\s+"
        r".+?\s+"
        r"no valor de\s+"
        r"R\$\s*([\d\.]+,\d{2})",
        full_text,
        re.IGNORECASE | re.DOTALL,
    )

    if total_match:
        total_amount = converter_valor_brasileiro(
            f"R$ {total_match.group(1)}"
        )

    due_date_match = re.search(
        r"Data de vencimento:\s*"
        r"(\d{2}\s+[A-Z]{3}\s+\d{4})",
        full_text,
        re.IGNORECASE,
    )

    if due_date_match:
        due_date = due_date_match.group(1)

    period_match = re.search(
        r"Período vigente:\s*"
        r"(\d{2}\s+[A-Z]{3})"
        r"\s+a\s+"
        r"(\d{2}\s+[A-Z]{3})",
        full_text,
        re.IGNORECASE,
    )

    if period_match:
        period_start = period_match.group(1)
        period_end = period_match.group(2)

    return MetadadosFatura(
        total_amount=total_amount,
        due_date=due_date,
        period_start=period_start,
        period_end=period_end,
    )


def gerar_resumo_das_transacoes(
    transactions: list[TransacaoAnalisada],
) -> dict[str, int]:

    summary = {
        "compra": 0,
        "estorno": 0,
        "pagamento": 0,
        "financiamento": 0,
    }

    for transaction in transactions:
        if transaction.type in summary:
            summary[transaction.type] += 1

    return summary


def gerar_resumo_por_categoria(
    transactions: list[TransacaoAnalisada],
) -> list[dict]:

    category_data: dict[str, dict] = {}

    for transaction in transactions:

        if transaction.type not in [
            "compra",
            "estorno",
        ]:
            continue

        category = transaction.category

        if category not in category_data:
            category_data[category] = {
                "category": category,
                "total_transactions": 0,
                "total_amount": 0.0,
            }

        category_data[category]["total_transactions"] += 1

        category_data[category]["total_amount"] += (
            transaction.amount
        )

    result = list(
        category_data.values()
    )

    for item in result:
        item["total_amount"] = round(
            item["total_amount"],
            2,
        )

    result.sort(
        key=lambda item: item["total_amount"],
        reverse=True,
    )

    return result