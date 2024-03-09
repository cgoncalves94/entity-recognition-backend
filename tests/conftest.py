from src.auth.service import delete_user_by_email  
from typing import Any, Generator, AsyncGenerator

import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient

from src.main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[TestClient, None]:
    host, port = "127.0.0.1", "9000"
    scope = {"client": (host, port)}

    async with TestClient(app, scope=scope) as client:
        yield client
        
@pytest_asyncio.fixture
async def user_cleanup():
    # No setup needed before yielding
    yield
    # Cleanup: Delete the test user after the test runs
    await delete_user_by_email("email@fake.com")