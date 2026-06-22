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