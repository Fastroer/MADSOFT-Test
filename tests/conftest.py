import os
import asyncio
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.dependencies import get_session
from db.models import Base, Meme
from s3.minio_client import minio_client
from public_api.app.main import public_app
from private_api.app.main import private_app

DATABASE_URL = "postgresql+asyncpg://root:root@test_db:5432/test_db"
MINIO_BUCKET_NAME = "test-memes"

os.environ["MINIO_BUCKET_NAME"] = MINIO_BUCKET_NAME

engine_test = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

public_app.dependency_overrides[get_session] = override_get_async_session
private_app.dependency_overrides[get_session] = override_get_async_session

@pytest.fixture(scope="function", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
@pytest.fixture(scope="function", autouse=True)
async def clear_minio_bucket():
    yield
    bucket_name = "test-memes"
    objects = minio_client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        minio_client.remove_object(bucket_name, obj.object_name)
    

@pytest.fixture(scope="session")
async def ac_public() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=public_app), base_url="http://test-public:8000") as ac:
        yield ac

@pytest.fixture(scope="session")
async def ac_private() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=private_app), base_url="http://test-private:8001") as ac:
        yield ac

@pytest.fixture(scope="session")
def asyncio_loop():
    """Create an instance of the default asyncio event loop for the session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
