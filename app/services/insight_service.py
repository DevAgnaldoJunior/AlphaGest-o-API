from collections import defaultdict

from app.models.transaction import Transacao

from app.services.dashboard_service import (
    obter_compras,
)

from app.services.merchant_normalizer import (
    normalizar_estabelecimento,
)


MINIMUM_SAMPLE_FOR_ANOMALY = 8

OTHER_CATEGORY_WARNING_PERCENTAGE = 15.0

MERCHANT_CATEGORY_CONCENTRATION_PERCENTAGE = 45.0


PRIORIDADE_POR_TIPO = {
    "alta_participacao_outros": 100,

    "pequenas_compras": 95,

    "compra_fora_do_padrao": 90,

    "concentracao_estabelecimento_categoria": 85,

    "concentracao_cartao": 80,

    "estabelecimento_recorrente": 75,

    "financiamentos": 70,

    "compras_sem_cartao_identificado": 65,

    "concentracao_categoria": 60,
}


GRUPOS_DE_REDUNDANCIA = [
    {
        "estabelecimento_recorrente",
        "concentracao_estabelecimento_categoria",
    },
]


def gerar_insight_pequenas_compras(
    small_purchases: dict,
    total_purchases: int,
) -> dict | None:

    total_transactions = small_purchases[
        "total_transactions"
    ]

    total_amount = small_purchases[
        "total_amount"
    ]

    spending_percentage = small_purchases[
        "percentage_of_spending"
    ]

    transaction_percentage = small_purchases[
        "percentage_of_transactions"
    ]

    if total_transactions < 5:
        return None

    if total_amount < 50:
        return None

    return {
        "type": "pequenas_compras",

        "severity": "informacao",

        "title": "Pequenas compras acumuladas",

        "message": (
            f"{total_transactions} das "
            f"{total_purchases} compras do período, "
            f"ou {transaction_percentage:.1f}%, "
            f"tiveram valor de até R$ 15. "
            f"Embora pequenas individualmente, "
            f"somaram R$ {total_amount:.2f}, "
            f"equivalentes a "
            f"{spending_percentage:.1f}% "
            f"dos gastos analisados."
        ),

        "metric_value": total_amount,
    }


def gerar_insight_categoria_outros(
    category_distribution: list[dict],
) -> dict | None:

    others = next(
        (
            item
            for item in category_distribution
            if item["category"].lower() == "outros"
        ),
        None,
    )

    if others is None:
        return None

    percentage = others[
        "percentage"
    ]

    if (
        percentage
        <
        OTHER_CATEGORY_WARNING_PERCENTAGE
    ):
        return None

    amount = others[
        "total_amount"
    ]

    total_transactions = others[
        "total_transactions"
    ]

    return {
        "type": "alta_participacao_outros",

        "severity": "atencao",

        "title": (
            "Parte relevante dos gastos "
            "não está categorizada"
        ),

        "message": (
            f"{total_transactions} transações "
            f"classificadas como Outros somam "
            f"R$ {amount:.2f} e representam "
            f"{percentage:.1f}% dos gastos "
            f"analisados. Revisar essas transações "
            f"pode melhorar a compreensão da "
            f"distribuição das despesas."
        ),

        "metric_value": percentage,
    }


def gerar_insight_concentracao_categoria(
    category_distribution: list[dict],
) -> dict | None:

    if not category_distribution:
        return None

    main_category = category_distribution[0]

    category = main_category[
        "category"
    ]

    percentage = main_category[
        "percentage"
    ]

    amount = main_category[
        "total_amount"
    ]

    if category.lower() == "outros":
        return None

    if percentage < 30:
        return None

    return {
        "type": "concentracao_categoria",

        "severity": "informacao",

        "title": (
            f"Maior concentração em {category}"
        ),

        "message": (
            f"{category} representa "
            f"{percentage:.1f}% dos gastos "
            f"analisados, totalizando "
            f"R$ {amount:.2f}."
        ),

        "metric_value": percentage,
    }


def gerar_insight_estabelecimento_recorrente(
    merchant_ranking: list[dict],
    total_purchases: int,
) -> dict | None:

    if not merchant_ranking:
        return None

    merchant = merchant_ranking[0]

    total_transactions = merchant[
        "total_transactions"
    ]

    if total_transactions < 3:
        return None

    merchant_name = merchant[
        "merchant"
    ]

    total_amount = merchant[
        "total_amount"
    ]

    average_ticket = merchant[
        "average_ticket"
    ]

    frequency_percentage = 0.0

    if total_purchases > 0:

        frequency_percentage = round(
            (
                total_transactions
                /
                total_purchases
            )
            *
            100,
            2,
        )

    return {
        "type": "estabelecimento_recorrente",

        "severity": "informacao",

        "title": "Estabelecimento mais recorrente",

        "message": (
            f"{merchant_name} apareceu em "
            f"{total_transactions} das "
            f"{total_purchases} compras realizadas, "
            f"representando "
            f"{frequency_percentage:.1f}% da "
            f"frequência de compras. "
            f"As transações somaram "
            f"R$ {total_amount:.2f}, "
            f"com ticket médio de "
            f"R$ {average_ticket:.2f}."
        ),

        "metric_value": total_amount,
    }


def gerar_insight_concentracao_cartao(
    card_distribution: list[dict],
) -> dict | None:

    if not card_distribution:
        return None

    main_card = card_distribution[0]

    percentage = main_card[
        "percentage"
    ]

    if percentage < 50:
        return None

    card = main_card[
        "card"
    ]

    amount = main_card[
        "total_amount"
    ]

    return {
        "type": "concentracao_cartao",

        "severity": "informacao",

        "title": "Concentração de gastos por cartão",

        "message": (
            f"O cartão final {card} concentrou "
            f"{percentage:.1f}% dos gastos entre "
            f"as compras com cartão identificável, "
            f"totalizando R$ {amount:.2f}."
        ),

        "metric_value": percentage,
    }


def gerar_insight_compras_sem_cartao(
    purchases_without_card: dict,
) -> dict | None:

    total_transactions = purchases_without_card[
        "total_transactions"
    ]

    total_amount = purchases_without_card[
        "total_amount"
    ]

    percentage = purchases_without_card[
        "percentage_of_spending"
    ]

    if total_transactions == 0:
        return None

    if percentage < 5:
        return None

    return {
        "type": "compras_sem_cartao_identificado",

        "severity": "informacao",

        "title": (
            "Parte dos gastos não possui "
            "cartão identificado"
        ),

        "message": (
            f"{total_transactions} compras sem "
            f"final de cartão identificado somam "
            f"R$ {total_amount:.2f}, equivalentes "
            f"a {percentage:.1f}% dos gastos "
            f"analisados."
        ),

        "metric_value": percentage,
    }


def gerar_insight_financiamentos(
    financing: dict,
) -> dict | None:

    total_transactions = financing[
        "total_transactions"
    ]

    total_amount = financing[
        "total_amount"
    ]

    if total_transactions == 0:
        return None

    return {
        "type": "financiamentos",

        "severity": "informacao",

        "title": (
            "Lançamentos relacionados "
            "a financiamentos"
        ),

        "message": (
            f"Foram identificados "
            f"{total_transactions} lançamentos "
            f"relacionados a financiamentos, "
            f"totalizando R$ {total_amount:.2f}. "
            f"Esse valor é apresentado "
            f"separadamente das compras comuns."
        ),

        "metric_value": total_amount,
    }


def gerar_insight_estabelecimento_na_categoria(
    transactions: list[Transacao],
) -> dict | None:

    purchases = obter_compras(
        transactions
    )

    if not purchases:
        return None

    category_totals: dict[
        str,
        float,
    ] = defaultdict(
        float
    )

    merchant_category_data = defaultdict(
        lambda: {
            "total_amount": 0.0,
            "total_transactions": 0,
        }
    )

    for transaction in purchases:

        category = transaction.category

        if category.lower() == "outros":
            continue

        merchant = normalizar_estabelecimento(
            transaction.description
        )

        category_totals[
            category
        ] += transaction.amount

        key = (
            category,
            merchant,
        )

        merchant_category_data[key][
            "total_amount"
        ] += transaction.amount

        merchant_category_data[key][
            "total_transactions"
        ] += 1

    candidates: list[dict] = []

    for (
        category,
        merchant,
    ), data in merchant_category_data.items():

        category_total = category_totals[
            category
        ]

        if category_total <= 0:
            continue

        percentage = (
            data["total_amount"]
            /
            category_total
        ) * 100

        if (
            percentage
            <
            MERCHANT_CATEGORY_CONCENTRATION_PERCENTAGE
        ):
            continue

        if data["total_transactions"] < 3:
            continue

        candidates.append(
            {
                "category": category,

                "merchant": merchant,

                "percentage": round(
                    percentage,
                    2,
                ),

                "total_amount": round(
                    data["total_amount"],
                    2,
                ),

                "total_transactions": (
                    data["total_transactions"]
                ),
            }
        )

    if not candidates:
        return None

    main_candidate = max(
        candidates,
        key=lambda item: item["percentage"],
    )

    return {
        "type": (
            "concentracao_estabelecimento_categoria"
        ),

        "severity": "informacao",

        "title": (
            f"Concentração dentro de "
            f"{main_candidate['category']}"
        ),

        "message": (
            f"{main_candidate['merchant']} respondeu "
            f"por {main_candidate['percentage']:.1f}% "
            f"dos gastos da categoria "
            f"{main_candidate['category']}, "
            f"somando "
            f"R$ {main_candidate['total_amount']:.2f} "
            f"em "
            f"{main_candidate['total_transactions']} "
            f"compras."
        ),

        "metric_value": (
            main_candidate["percentage"]
        ),
    }


def calcular_quartil(
    values: list[float],
    percentile: float,
) -> float:

    if not values:
        return 0.0

    ordered_values = sorted(
        values
    )

    position = (
        len(ordered_values) - 1
    ) * percentile

    lower_index = int(
        position
    )

    upper_index = min(
        lower_index + 1,
        len(ordered_values) - 1,
    )

    fraction = (
        position
        -
        lower_index
    )

    lower_value = ordered_values[
        lower_index
    ]

    upper_value = ordered_values[
        upper_index
    ]

    return (
        lower_value
        +
        (
            upper_value
            -
            lower_value
        )
        *
        fraction
    )


def gerar_insight_compra_fora_do_padrao(
    transactions: list[Transacao],
) -> dict | None:

    purchases = obter_compras(
        transactions
    )

    category_groups: dict[
        str,
        list[Transacao],
    ] = {}

    for transaction in purchases:

        if transaction.category.lower() == "outros":
            continue

        category_groups.setdefault(
            transaction.category,
            [],
        )

        category_groups[
            transaction.category
        ].append(
            transaction
        )

    anomalies: list[
        tuple[Transacao, float]
    ] = []

    for category_transactions in (
        category_groups.values()
    ):

        if (
            len(category_transactions)
            <
            MINIMUM_SAMPLE_FOR_ANOMALY
        ):
            continue

        values = [
            transaction.amount
            for transaction in category_transactions
        ]

        q1 = calcular_quartil(
            values,
            0.25,
        )

        q3 = calcular_quartil(
            values,
            0.75,
        )

        iqr = q3 - q1

        if iqr <= 0:
            continue

        upper_limit = (
            q3
            +
            1.5
            *
            iqr
        )

        for transaction in category_transactions:

            if transaction.amount > upper_limit:

                anomalies.append(
                    (
                        transaction,
                        upper_limit,
                    )
                )

    if not anomalies:
        return None

    most_relevant = max(
        anomalies,
        key=lambda item: (
            item[0].amount
            -
            item[1]
        ),
    )

    transaction = most_relevant[0]

    return {
        "type": "compra_fora_do_padrao",

        "severity": "atencao",

        "title": "Compra acima do padrão da categoria",

        "message": (
            f"A transação "
            f"\"{transaction.description}\" "
            f"de R$ {transaction.amount:.2f} "
            f"está significativamente acima do "
            f"padrão observado na categoria "
            f"{transaction.category}."
        ),

        "metric_value": transaction.amount,
    }


def gerar_insights(
    transactions: list[Transacao],
    category_distribution: list[dict],
    card_distribution: list[dict],
    merchant_ranking: list[dict],
    small_purchases: dict,
    purchases_without_card: dict,
    financing: dict,
) -> list[dict]:

    purchases = obter_compras(
        transactions
    )

    total_purchases = len(
        purchases
    )

    possible_insights = [
        gerar_insight_pequenas_compras(
            small_purchases=small_purchases,
            total_purchases=total_purchases,
        ),

        gerar_insight_categoria_outros(
            category_distribution
        ),

        gerar_insight_concentracao_categoria(
            category_distribution
        ),

        gerar_insight_estabelecimento_recorrente(
            merchant_ranking=merchant_ranking,
            total_purchases=total_purchases,
        ),

        gerar_insight_estabelecimento_na_categoria(
            transactions
        ),

        gerar_insight_concentracao_cartao(
            card_distribution
        ),

        gerar_insight_compras_sem_cartao(
            purchases_without_card
        ),

        gerar_insight_financiamentos(
            financing
        ),

        gerar_insight_compra_fora_do_padrao(
            transactions
        ),
    ]

    insights: list[dict] = []

    for insight in possible_insights:

        if insight is not None:

            insights.append(
                insight
            )

    return insights


def obter_prioridade_do_insight(
    insight: dict,
) -> int:

    insight_type = insight[
        "type"
    ]

    base_priority = PRIORIDADE_POR_TIPO.get(
        insight_type,
        0,
    )

    severity = insight.get(
        "severity"
    )

    severity_bonus = 0

    if severity == "atencao":
        severity_bonus = 5

    return (
        base_priority
        +
        severity_bonus
    )


def existe_conflito_de_redundancia(
    insight: dict,
    featured_insights: list[dict],
) -> bool:

    insight_type = insight[
        "type"
    ]

    featured_types = {
        featured["type"]
        for featured in featured_insights
    }

    for group in GRUPOS_DE_REDUNDANCIA:

        if insight_type not in group:
            continue

        types_already_featured = (
            featured_types
            &
            group
        )

        if types_already_featured:
            return True

    return False


def separar_insights_por_prioridade(
    insights: list[dict],
    featured_limit: int = 4,
) -> tuple[
    list[dict],
    list[dict],
]:

    ordered_insights = sorted(
        insights,
        key=obter_prioridade_do_insight,
        reverse=True,
    )

    featured_insights: list[dict] = []

    additional_insights: list[dict] = []

    for insight in ordered_insights:

        if len(
            featured_insights
        ) >= featured_limit:

            additional_insights.append(
                insight
            )

            continue

        redundant = (
            existe_conflito_de_redundancia(
                insight=insight,
                featured_insights=featured_insights,
            )
        )

        if redundant:

            additional_insights.append(
                insight
            )

            continue

        featured_insights.append(
            insight
        )

    return (
        featured_insights,
        additional_insights,
    )