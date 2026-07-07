from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.dashboard import (
    router as dashboard_router,
)

from app.api.routes.health import (
    router as health_router,
)

from app.api.routes.faturas import (
    router as invoices_router,
)

from app.api.routes.transactions import (
    router as transactions_router,
)

from app.database.database import (
    criar_tabelas,
)

import app.models


@asynccontextmanager
async def gerenciar_ciclo_de_vida(
    app: FastAPI,
):

    criar_tabelas()

    yield


app = FastAPI(
    title="Alpha API",
    description=(
        "API para organização financeira, "
        "processamento de faturas e "
        "análise de comportamento financeiro."
    ),
    version="1.0.0",
    lifespan=gerenciar_ciclo_de_vida,
)


app.include_router(
    health_router,
    prefix="/api/v1",
)


app.include_router(
    invoices_router,
    prefix="/api/v1",
)


app.include_router(
    transactions_router,
    prefix="/api/v1",
)


app.include_router(
    dashboard_router,
    prefix="/api/v1",
)