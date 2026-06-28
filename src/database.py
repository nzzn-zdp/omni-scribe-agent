from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, inspect
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
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        
        # 检查并添加新字段（仅对SQLite）
        if "sqlite" in settings.database_url:
            try:
                # 使用run_sync执行PRAGMA
                def check_and_add_columns(sync_conn):
                    # 检查现有列
                    result = sync_conn.execute(text("PRAGMA table_info(system_configs)"))
                    columns = [row[1] for row in result.fetchall()]
                    
                    if 'help' not in columns:
                        sync_conn.execute(text("ALTER TABLE system_configs ADD COLUMN help TEXT"))
                    if 'platform' not in columns:
                        sync_conn.execute(text("ALTER TABLE system_configs ADD COLUMN platform VARCHAR(100)"))
                
                await conn.run_sync(check_and_add_columns)
                print("数据库表结构更新完成")
            except Exception as e:
                print(f"更新表结构时出错: {e}")