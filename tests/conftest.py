import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.database import Base, get_db
from src.main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(engine):
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
async def client():
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client