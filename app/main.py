from fastapi import FastAPI

from app.api.routes.health import router as health_router


app = FastAPI(
    title="Financial API",
    description="API para organização financeira e processamento de faturas.",
    version="1.0.0",
)


app.include_router(
    health_router,
    prefix="/api/v1",
)