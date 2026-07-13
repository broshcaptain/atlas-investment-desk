from fastapi import FastAPI

from backend.routes.companies import router as companies_router
from backend.routes.dashboard import router as dashboard_router

app = FastAPI(title="Atlas API")

app.include_router(dashboard_router)
app.include_router(companies_router)
