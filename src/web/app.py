from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

# 创建FastAPI应用
app = FastAPI(title="OmniScribeAgent Web管理界面")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# 模板配置
templates = Jinja2Templates(directory="src/web/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/hotspots", response_class=HTMLResponse)
async def hotspots_page(request: Request):
    """热点监控页面"""
    return templates.TemplateResponse("hotspots.html", {"request": request})

@app.get("/content", response_class=HTMLResponse)
async def content_page(request: Request):
    """内容生产页面"""
    return templates.TemplateResponse("content.html", {"request": request})

@app.get("/publish", response_class=HTMLResponse)
async def publish_page(request: Request):
    """发布管理页面"""
    return templates.TemplateResponse("publish.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """系统设置页面"""
    return templates.TemplateResponse("settings.html", {"request": request})