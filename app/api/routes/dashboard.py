from datetime import date as Date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.database.database import obter_sessao

from app.services.user_login.auth_service import (
    obter_usuario_autenticado,
)

from app.schemas.dashboard import (
    RespostaComportamento,
    RespostaComprasSemCartao,
    RespostaDashboard,
    RespostaDistribuicaoCartao,
    RespostaDistribuicaoCategoria,
    RespostaEstabelecimento,
    RespostaEstornos,
    RespostaFiltrosDashboard,
    RespostaFinanciamentos,
    RespostaInsight,
    RespostaMaiorCompra,
    RespostaPequenasCompras,
    RespostaVisaoGeral,
)

from app.services.dashboard_service import (
    calcular_compras_sem_cartao,
    calcular_distribuicao_por_cartao,
    calcular_distribuicao_por_categoria,
    calcular_estornos,
    calcular_financiamentos,
    calcular_gasto_liquido,
    calcular_pequenas_compras,
    calcular_ranking_estabelecimentos,
    calcular_ticket_medio,
    calcular_total_gasto,
    obter_compras,
    obter_maior_compra,
)

from app.services.insight_service import (
    gerar_insights,
    separar_insights_por_prioridade,
)

from app.services.transaction_repository import (
    filtrar_transacoes,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[
        Depends(
            obter_usuario_autenticado
        )
    ],
)


@router.get(
    "",
    response_model=RespostaDashboard,
)
def consultar_dashboard(
    invoice_id: int | None = Query(
        default=None,
    ),

    card: str | None = Query(
        default=None,
    ),

    category: str | None = Query(
        default=None,
    ),

    start_date: Date | None = Query(
        default=None,
    ),

    end_date: Date | None = Query(
        default=None,
    ),

    session: Session = Depends(
        obter_sessao
    ),

) -> RespostaDashboard:

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
        category=category,
        start_date=start_date,
        end_date=end_date,
    )

    purchases = obter_compras(
        transactions
    )

    total_spent = calcular_total_gasto(
        transactions
    )

    net_spent = calcular_gasto_liquido(
        transactions
    )

    average_ticket = calcular_ticket_medio(
        transactions
    )

    largest_purchase = obter_maior_compra(
        transactions
    )

    category_distribution = (
        calcular_distribuicao_por_categoria(
            transactions
        )
    )

    card_distribution = (
        calcular_distribuicao_por_cartao(
            transactions
        )
    )

    merchant_ranking = (
        calcular_ranking_estabelecimentos(
            transactions
        )
    )

    small_purchases = calcular_pequenas_compras(
        transactions
    )

    refunds = calcular_estornos(
        transactions
    )

    financing = calcular_financiamentos(
        transactions
    )

    purchases_without_card = (
        calcular_compras_sem_cartao(
            transactions
        )
    )

    insights = gerar_insights(
        transactions=transactions,

        category_distribution=(
            category_distribution
        ),

        card_distribution=(
            card_distribution
        ),

        merchant_ranking=(
            merchant_ranking
        ),

        small_purchases=(
            small_purchases
        ),

        purchases_without_card=(
            purchases_without_card
        ),

        financing=financing,
    )

    (
        featured_insights,
        additional_insights,
    ) = separar_insights_por_prioridade(
        insights=insights,
        featured_limit=4,
    )

    largest_purchase_response = None

    if largest_purchase is not None:

        largest_purchase_response = (
            RespostaMaiorCompra(
                transaction_id=(
                    largest_purchase.id
                ),

                description=(
                    largest_purchase.description
                ),

                amount=(
                    largest_purchase.amount
                ),

                category=(
                    largest_purchase.category
                ),

                date=(
                    largest_purchase.transaction_date
                ),
            )
        )

    return RespostaDashboard(

        filters=RespostaFiltrosDashboard(
            invoice_id=invoice_id,

            card=card,

            category=category,

            start_date=start_date,

            end_date=end_date,
        ),

        overview=RespostaVisaoGeral(
            total_spent=total_spent,

            net_spent=net_spent,

            total_purchases=len(
                purchases
            ),

            average_ticket=average_ticket,

            largest_purchase=(
                largest_purchase_response
            ),
        ),

        category_distribution=[
            RespostaDistribuicaoCategoria(
                category=item[
                    "category"
                ],

                total_amount=item[
                    "total_amount"
                ],

                percentage=item[
                    "percentage"
                ],

                total_transactions=item[
                    "total_transactions"
                ],
            )
            for item in category_distribution
        ],

        card_distribution=[
            RespostaDistribuicaoCartao(
                card=item[
                    "card"
                ],

                total_amount=item[
                    "total_amount"
                ],

                percentage=item[
                    "percentage"
                ],

                total_transactions=item[
                    "total_transactions"
                ],
            )
            for item in card_distribution
        ],

        merchant_ranking=[
            RespostaEstabelecimento(
                merchant=item[
                    "merchant"
                ],

                total_transactions=item[
                    "total_transactions"
                ],

                total_amount=item[
                    "total_amount"
                ],

                average_ticket=item[
                    "average_ticket"
                ],
            )
            for item in merchant_ranking
        ],

        behavior=RespostaComportamento(

            small_purchases=RespostaPequenasCompras(
                threshold=small_purchases[
                    "threshold"
                ],

                total_transactions=small_purchases[
                    "total_transactions"
                ],

                total_amount=small_purchases[
                    "total_amount"
                ],

                percentage_of_spending=small_purchases[
                    "percentage_of_spending"
                ],

                percentage_of_transactions=small_purchases[
                    "percentage_of_transactions"
                ],
            ),

            refunds=RespostaEstornos(
                total_transactions=refunds[
                    "total_transactions"
                ],

                total_amount=refunds[
                    "total_amount"
                ],
            ),

            financing=RespostaFinanciamentos(
                total_transactions=financing[
                    "total_transactions"
                ],

                total_amount=financing[
                    "total_amount"
                ],
            ),

            purchases_without_card=RespostaComprasSemCartao(
                total_transactions=(
                    purchases_without_card[
                        "total_transactions"
                    ]
                ),

                total_amount=(
                    purchases_without_card[
                        "total_amount"
                    ]
                ),

                percentage_of_spending=(
                    purchases_without_card[
                        "percentage_of_spending"
                    ]
                ),
            ),
        ),

        featured_insights=[
            RespostaInsight(
                type=item[
                    "type"
                ],

                severity=item[
                    "severity"
                ],

                title=item[
                    "title"
                ],

                message=item[
                    "message"
                ],

                metric_value=item[
                    "metric_value"
                ],
            )
            for item in featured_insights
        ],

        additional_insights=[
            RespostaInsight(
                type=item[
                    "type"
                ],

                severity=item[
                    "severity"
                ],

                title=item[
                    "title"
                ],

                message=item[
                    "message"
                ],

                metric_value=item[
                    "metric_value"
                ],
            )
            for item in additional_insights
        ],
    )