### 任务1：项目基础架构搭建

**Files:**
- Create: `src/__init__.py`
- Create: `src/main.py`
- Create: `src/config.py`
- Create: `src/database.py`
- Create: `requirements.txt`
- Create: `docker-compose.yml`
- Create: `Dockerfile`
- Create: `README.md`

**Interfaces:**
- Produces: 基础项目结构，配置管理，数据库连接

- [ ] **步骤1：创建项目结构**

```bash
mkdir -p src/models src/core src/hotspot/adapters src/content src/publish/adapters src/api src/web/static src/web/templates tests/test_hotspot tests/test_content tests/test_publish tests/test_api data/db data/logs data/logs config
```

- [ ] **步骤2：创建requirements.txt**

```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
redis==5.0.1
pydantic==2.5.2
pydantic-settings==2.1.0
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.23.2
python-multipart==0.0.6
jinja2==3.1.2
python-dotenv==1.0.0
```

- [ ] **步骤3：创建配置管理模块**

```python
# src/config.py
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional
import yaml
from pathlib import Path

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "OmniScribeAgent"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./data/db/omniscribe.db"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # LLM配置
    llm_providers: Dict[str, Dict] = {
        "openai": {
            "api_key": "",
            "model": "gpt-4",
            "max_tokens": 4096
        },
        "claude": {
            "api_key": "",
            "model": "claude-3-opus-20240229",
            "max_tokens": 4096
        }
    }
    
    # 热点监控配置
    hotspot_check_interval: int = 300  # 5分钟
    hotspot_min_score: float = 0.6
    
    # 发布配置
    publish_retry_count: int = 3
    publish_retry_delay: int = 60  # 1分钟
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def load_platform_config(platform_name: str) -> Dict:
    """加载平台配置"""
    config_path = Path("config/platforms.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config.get(platform_name, {})
    return {}

settings = Settings()
```

- [ ] **步骤4：创建数据库模块**

```python
# src/database.py
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
```

- [ ] **步骤5：创建主应用入口**

```python
# src/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .config import settings
from .database import init_db
from .api import hotspot, content, publish, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理资源
    pass

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="端到端自动化内容生产与分发Agent",
    lifespan=lifespan
)

# 注册路由
app.include_router(hotspot.router, prefix="/api/hotspots", tags=["热点监控"])
app.include_router(content.router, prefix="/api/content", tags=["内容生产"])
app.include_router(publish.router, prefix="/api/publish", tags=["多平台发布"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理接口"])

@app.get("/")
async def root():
    return {"message": f"欢迎使用 {settings.app_name}"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}
```

- [ ] **步骤6：创建Docker配置**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/db/omniscribe.db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

- [ ] **步骤7：运行测试验证基础架构**

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/ -v

# 启动应用
uvicorn src.main:app --reload
```

- [ ] **步骤8：提交基础架构代码**

```bash
git add .
git commit -m "feat: 初始化项目基础架构"
```