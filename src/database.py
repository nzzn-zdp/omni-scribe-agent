from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from .config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # 检查并添加新字段
        try:
            # 获取现有列信息
            result = await conn.execute("PRAGMA table_info(system_configs)")
            columns = [row[1] for row in result.fetchall()]
            
            if 'help' not in columns:
                await conn.execute("ALTER TABLE system_configs ADD COLUMN help TEXT")
            if 'platform' not in columns:
                await conn.execute("ALTER TABLE system_configs ADD COLUMN platform VARCHAR(100)")
        except Exception as e:
            print(f"更新表结构时出错: {e}")