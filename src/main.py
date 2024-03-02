from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware

from database import Database  # Ensure this path is correct
from auth.router import router as auth_router
from nlp.router import router as nlp_router
from config import app_configs, settings

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Startup
    await Database.connect(settings.DATABASE_URL, settings.DATABASE_NAME)  

    yield

    # Shutdown
    await Database.close()

app = FastAPI(**app_configs, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=settings.CORS_HEADERS,
)

if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT.value,  # Ensure this correctly references the environment string
    )

@app.get("/")
async def root():
    return {"message": "Welcome to my FastAPI application!"}


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(nlp_router, prefix="/nlp", tags=["NLP"])
