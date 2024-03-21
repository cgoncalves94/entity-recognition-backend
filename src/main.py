from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.config import app_configs, settings
from src.database import Database
from src.nlp.config import nlp_config
from src.nlp.models import load_bertopic_model, load_embeddings_model
from src.nlp.router import router as nlp_router


# Define an async context manager for the lifespan of the FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Context manager for managing the lifespan of the application.

    Args:
      app (FastAPI): The FastAPI application instance.

    Yields:
      None

    Raises:
      Exception: If there is an error connecting to the database.

    """
    try:
        # Startup
        await Database.connect(settings.DATABASE_URL, settings.DATABASE_NAME)

        # Load BERTopic model and assign it to the application state
        model_object_name = nlp_config.MODEL_NAME
        app.state.bertopic_model = await load_bertopic_model(model_object_name)
        print("BERTopic model loaded successfully. ")

        # Load transformers model and assign it to the application state
        app.state.tokenizer, app.state.model = await load_embeddings_model()
        print("Embeddings model loaded successfully.")

        yield

    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        import traceback

        traceback.print_exc()  # Print the full traceback
    finally:
        # Shutdown
        Database.close()


# Create a FastAPI application instance with the specified configurations and lifespan
app = FastAPI(**app_configs, lifespan=lifespan)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=settings.CORS_HEADERS,
)

# Initialize Sentry for error tracking if the application is deployed
if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT.value,  # Ensure this correctly references the environment string
    )


# Define the root endpoint
@app.get("/")
async def root():
    """
    Root endpoint of the FastAPI application.
    Returns a welcome message.
    """
    return {"message": "Welcome to my FastAPI application!"}


# Define the healthcheck endpoint
@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    """
    Healthcheck endpoint of the FastAPI application.
    Returns the status of the application.
    """
    return {"status": "ok"}


# Include the auth router with the specified prefix and tags
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# Include the NLP router with the specified prefix and tags
app.include_router(nlp_router, prefix="/nlp", tags=["NLP"])
