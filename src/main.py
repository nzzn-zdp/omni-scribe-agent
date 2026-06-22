from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from pathlib import Path
from .config import settings, load_configs_from_db
from .database import init_db
from .api import hotspot, content, publish, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    # 从数据库加载配置
    await load_configs_from_db()
    yield
    # 关闭时清理资源
    pass

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="端到端自动化内容生产与分发Agent",
    lifespan=lifespan
)

# 挂载静态文件
Path("src/web/static").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# 模板配置
Path("src/web/templates").mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory="src/web/templates")

# 注册API路由
app.include_router(hotspot.router, prefix="/api/hotspots", tags=["热点监控"])
app.include_router(content.router, prefix="/api/content", tags=["内容生产"])
app.include_router(publish.router, prefix="/api/publish", tags=["多平台发布"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理接口"])

# Web页面路由
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """系统设置页面"""
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": settings.app_version}