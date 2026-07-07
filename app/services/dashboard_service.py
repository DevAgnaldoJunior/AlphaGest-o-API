from collections import defaultdict

from app.models.transaction import Transacao

from app.services.merchant_normalizer import (
    normalizar_estabelecimento,
)


SMALL_PURCHASE_THRESHOLD = 15.0


def obter_compras(
    transactions: list[Transacao],
) -> list[Transacao]:

    return [
        transaction
        for transaction in transactions
        if transaction.type == "compra"
    ]


def obter_estornos(
    transactions: list[Transacao],
) -> list[Transacao]:

    return [
        transaction
        for transaction in transactions
        if transaction.type == "estorno"
    ]


def obter_financiamentos(
    transactions: list[Transacao],
) -> list[Transacao]:

    return [
        transaction
        for transaction in transactions
        if transaction.type == "financiamento"
    ]


def calcular_total_gasto(
    transactions: list[Transacao],
) -> float:

    purchases = obter_compras(
        transactions
    )

    total = sum(
        transaction.amount
        for transaction in purchases
    )

    return round(
        total,
        2,
    )


def calcular_gasto_liquido(
    transactions: list[Transacao],
) -> float:

    purchases = obter_compras(
        transactions
    )

    refunds = obter_estornos(
        transactions
    )

    purchase_total = sum(
        transaction.amount
        for transaction in purchases
    )

    refund_total = sum(
        transaction.amount
        for transaction in refunds
    )

    net_total = (
        purchase_total
        +
        refund_total
    )

    return round(
        net_total,
        2,
    )


def calcular_ticket_medio(
    transactions: list[Transacao],
) -> float:

    purchases = obter_compras(
        transactions
    )

    if not purchases:
        return 0.0

    total = sum(
        transaction.amount
        for transaction in purchases
    )

    average = total / len(
        purchases
    )

    return round(
        average,
        2,
    )


def obter_maior_compra(
    transactions: list[Transacao],
) -> Transacao | None:

    purchases = obter_compras(
        transactions
    )

    if not purchases:
        return None

    return max(
        purchases,
        key=lambda transaction: transaction.amount,
    )


def calcular_distribuicao_por_categoria(
    transactions: list[Transacao],
) -> list[dict]:

    purchases = obter_compras(
        transactions
    )

    total_spent = sum(
        transaction.amount
        for transaction in purchases
    )

    category_data = defaultdict(
        lambda: {
            "total_amount": 0.0,
            "total_transactions": 0,
        }
    )

    for transaction in purchases:

        category = transaction.category

        category_data[category][
            "total_amount"
        ] += transaction.amount

        category_data[category][
            "total_transactions"
        ] += 1

    result: list[dict] = []

    for category, data in category_data.items():

        amount = round(
            data["total_amount"],
            2,
        )

        percentage = 0.0

        if total_spent > 0:

            percentage = round(
                (
                    amount
                    /
                    total_spent
                )
                *
                100,
                2,
            )

        result.append(
            {
                "category": category,
                "total_amount": amount,
                "percentage": percentage,
                "total_transactions": (
                    data["total_transactions"]
                ),
            }
        )

    result.sort(
        key=lambda item: item["total_amount"],
        reverse=True,
    )

    return result


def calcular_distribuicao_por_cartao(
    transactions: list[Transacao],
) -> list[dict]:

    purchases = obter_compras(
        transactions
    )

    identified_purchases = [
        transaction
        for transaction in purchases
        if transaction.card is not None
    ]

    total_identified = sum(
        transaction.amount
        for transaction in identified_purchases
    )

    card_data = defaultdict(
        lambda: {
            "total_amount": 0.0,
            "total_transactions": 0,
        }
    )

    for transaction in identified_purchases:

        card = transaction.card

        card_data[card][
            "total_amount"
        ] += transaction.amount

        card_data[card][
            "total_transactions"
        ] += 1

    result: list[dict] = []

    for card, data in card_data.items():

        amount = round(
            data["total_amount"],
            2,
        )

        percentage = 0.0

        if total_identified > 0:

            percentage = round(
                (
                    amount
                    /
                    total_identified
                )
                *
                100,
                2,
            )

        result.append(
            {
                "card": card,
                "total_amount": amount,
                "percentage": percentage,
                "total_transactions": (
                    data["total_transactions"]
                ),
            }
        )

    result.sort(
        key=lambda item: item["total_amount"],
        reverse=True,
    )

    return result


def calcular_compras_sem_cartao(
    transactions: list[Transacao],
) -> dict:

    purchases = obter_compras(
        transactions
    )

    purchases_without_card = [
        transaction
        for transaction in purchases
        if transaction.card is None
    ]

    total_without_card = sum(
        transaction.amount
        for transaction in purchases_without_card
    )

    total_spent = sum(
        transaction.amount
        for transaction in purchases
    )

    percentage = 0.0

    if total_spent > 0:

        percentage = round(
            (
                total_without_card
                /
                total_spent
            )
            *
            100,
            2,
        )

    return {
        "total_transactions": len(
            purchases_without_card
        ),

        "total_amount": round(
            total_without_card,
            2,
        ),

        "percentage_of_spending": percentage,
    }


def calcular_ranking_estabelecimentos(
    transactions: list[Transacao],
    limit: int = 10,
) -> list[dict]:

    purchases = obter_compras(
        transactions
    )

    merchant_data = defaultdict(
        lambda: {
            "total_amount": 0.0,
            "total_transactions": 0,
        }
    )

    for transaction in purchases:

        merchant = normalizar_estabelecimento(
            transaction.description
        )

        merchant_data[merchant][
            "total_amount"
        ] += transaction.amount

        merchant_data[merchant][
            "total_transactions"
        ] += 1

    result: list[dict] = []

    for merchant, data in merchant_data.items():

        total_amount = round(
            data["total_amount"],
            2,
        )

        total_transactions = (
            data["total_transactions"]
        )

        average_ticket = round(
            total_amount
            /
            total_transactions,
            2,
        )

        result.append(
            {
                "merchant": merchant,
                "total_transactions": (
                    total_transactions
                ),
                "total_amount": total_amount,
                "average_ticket": average_ticket,
            }
        )

    result.sort(
        key=lambda item: (
            item["total_transactions"],
            item["total_amount"],
        ),
        reverse=True,
    )

    return result[:limit]


def calcular_pequenas_compras(
    transactions: list[Transacao],
) -> dict:

    purchases = obter_compras(
        transactions
    )

    small_purchases = [
        transaction
        for transaction in purchases
        if transaction.amount
        <= SMALL_PURCHASE_THRESHOLD
    ]

    small_total = sum(
        transaction.amount
        for transaction in small_purchases
    )

    total_spent = sum(
        transaction.amount
        for transaction in purchases
    )

    spending_percentage = 0.0

    if total_spent > 0:

        spending_percentage = round(
            (
                small_total
                /
                total_spent
            )
            *
            100,
            2,
        )

    quantity_percentage = 0.0

    if purchases:

        quantity_percentage = round(
            (
                len(small_purchases)
                /
                len(purchases)
            )
            *
            100,
            2,
        )

    return {
        "threshold": SMALL_PURCHASE_THRESHOLD,

        "total_transactions": len(
            small_purchases
        ),

        "total_amount": round(
            small_total,
            2,
        ),

        "percentage_of_spending": (
            spending_percentage
        ),

        "percentage_of_transactions": (
            quantity_percentage
        ),
    }


def calcular_estornos(
    transactions: list[Transacao],
) -> dict:

    refunds = obter_estornos(
        transactions
    )

    total = sum(
        abs(transaction.amount)
        for transaction in refunds
    )

    return {
        "total_transactions": len(
            refunds
        ),

        "total_amount": round(
            total,
            2,
        ),
    }


def calcular_financiamentos(
    transactions: list[Transacao],
) -> dict:

    financing = obter_financiamentos(
        transactions
    )

    total = sum(
        transaction.amount
        for transaction in financing
    )

    return {
        "total_transactions": len(
            financing
        ),

        "total_amount": round(
            total,
            2,
        ),
    }