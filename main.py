from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.sessions.router import router as sessions_router
from src.shared.exceptions.global_exception import register_exception_handlers

app = FastAPI(
    docs_url="/api-docs",
    redoc_url=None,
    summary="MakeTravo Endpoints",
)

# Cookies require an explicit origin list — "*" is rejected by browsers
# whenever allow_credentials is on.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

register_exception_handlers(app)

app.include_router(sessions_router, prefix="/api/sessions", tags=["Sessions"])
