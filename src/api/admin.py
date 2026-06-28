from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List
from ..database import get_db
from ..models.hotspot import HotspotSource
from ..models.content import ContentTask
from ..models.publish import Platform, PublishRecord
from ..models.config import SystemConfig
from ..core.event_bus import event_bus
from ..core.task_queue import task_queue

router = APIRouter()

# 默认配置项
DEFAULT_CONFIGS = [
    # LLM配置
    {"key": "openai_api_key", "value": "", "description": "OpenAI API密钥", "help": "在 https://platform.openai.com/api-keys 获取", "category": "llm", "platform": "", "is_sensitive": True},
    {"key": "openai_model", "value": "gpt-4", "description": "OpenAI模型", "help": "可选: gpt-4, gpt-4-turbo, gpt-3.5-turbo", "category": "llm", "platform": "", "is_sensitive": False},
    {"key": "claude_api_key", "value": "", "description": "Claude API密钥", "help": "在 https://console.anthropic.com 获取", "category": "llm", "platform": "", "is_sensitive": True},
    {"key": "claude_model", "value": "claude-3-opus-20240229", "description": "Claude模型", "help": "可选: claude-3-opus, claude-3-sonnet, claude-3-haiku", "category": "llm", "platform": "", "is_sensitive": False},
    
    # 微信公众号配置
    {"key": "wechat_app_id", "value": "", "description": "AppID", "help": "在微信公众平台 https://mp.weixin.qq.com 设置与开发 > 基本配置中获取", "category": "platform", "platform": "wechat", "is_sensitive": False},
    {"key": "wechat_app_secret", "value": "", "description": "AppSecret", "help": "在微信公众平台设置与开发 > 基本配置中获取，需要管理员扫码确认", "category": "platform", "platform": "wechat", "is_sensitive": True},
    
    # 微博配置
    {"key": "weibo_access_token", "value": "", "description": "Access Token", "help": "在微博开放平台 https://open.weibo.com 创建应用后获取", "category": "platform", "platform": "weibo", "is_sensitive": True},
    
    # 知乎配置
    {"key": "zhihu_client_id", "value": "", "description": "Client ID", "help": "在知乎开放平台 https://open.zhihu.com 创建应用后获取", "category": "platform", "platform": "zhihu", "is_sensitive": False},
    {"key": "zhihu_client_secret", "value": "", "description": "Client Secret", "help": "在知乎开放平台创建应用后获取", "category": "platform", "platform": "zhihu", "is_sensitive": True},
    
    # 小红书配置
    {"key": "xiaohongshu_cookie", "value": "", "description": "Cookie", "help": "登录小红书网页版 https://www.xiaohongshu.com 后，从浏览器开发者工具中获取Cookie", "category": "platform", "platform": "xiaohongshu", "is_sensitive": True},
    
    # WordPress配置
    {"key": "wordpress_url", "value": "", "description": "站点地址", "help": "WordPress站点URL，如 https://your-site.com", "category": "platform", "platform": "wordpress", "is_sensitive": False},
    {"key": "wordpress_username", "value": "", "description": "用户名", "help": "WordPress管理员用户名", "category": "platform", "platform": "wordpress", "is_sensitive": False},
    {"key": "wordpress_password", "value": "", "description": "应用密码", "help": "在WordPress后台 > 用户 > 应用密码中生成，不要使用登录密码", "category": "platform", "platform": "wordpress", "is_sensitive": True},
    
    # 系统配置
    {"key": "hotspot_check_interval", "value": "300", "description": "热点检查间隔（秒）", "help": "系统自动检查热点的时间间隔，默认300秒（5分钟）", "category": "system", "platform": "", "is_sensitive": False},
    {"key": "hotspot_min_score", "value": "0.6", "description": "热点最低分数", "help": "只有评分高于此值的热点才会被处理，范围0-1", "category": "system", "platform": "", "is_sensitive": False},
    {"key": "publish_retry_count", "value": "3", "description": "发布重试次数", "help": "发布失败后的重试次数", "category": "system", "platform": "", "is_sensitive": False},
    {"key": "publish_retry_delay", "value": "60", "description": "发布重试延迟（秒）", "help": "每次重试之间的等待时间", "category": "system", "platform": "", "is_sensitive": False},
]

# 平台信息配置
PLATFORM_INFO = {
    "wechat": {
        "name": "微信公众号",
        "icon": "💬",
        "description": "发布文章到微信公众号",
        "docs_url": "https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html",
        "required_configs": ["wechat_app_id", "wechat_app_secret"],
        "setup_steps": [
            "1. 注册微信公众号（服务号或订阅号）",
            "2. 登录微信公众平台 https://mp.weixin.qq.com",
            "3. 进入 设置与开发 > 基本配置",
            "4. 获取 AppID 和 AppSecret",
            "5. 配置 IP 白名单"
        ]
    },
    "weibo": {
        "name": "微博",
        "icon": "📱",
        "description": "发布内容到微博",
        "docs_url": "https://open.weibo.com/wiki",
        "required_configs": ["weibo_access_token"],
        "setup_steps": [
            "1. 注册微博开放平台账号",
            "2. 创建应用 https://open.weibo.com",
            "3. 获取 Access Token",
            "4. 申请发布权限"
        ]
    },
    "zhihu": {
        "name": "知乎",
        "icon": "❓",
        "description": "发布文章到知乎",
        "docs_url": "https://open.zhihu.com/docs",
        "required_configs": ["zhihu_client_id", "zhihu_client_secret"],
        "setup_steps": [
            "1. 注册知乎开放平台账号",
            "2. 创建应用 https://open.zhihu.com",
            "3. 获取 Client ID 和 Client Secret",
            "4. 配置回调地址"
        ]
    },
    "xiaohongshu": {
        "name": "小红书",
        "icon": "📕",
        "description": "发布笔记到小红书",
        "docs_url": "",
        "required_configs": ["xiaohongshu_cookie"],
        "setup_steps": [
            "1. 登录小红书网页版 https://www.xiaohongshu.com",
            "2. 打开浏览器开发者工具（F12）",
            "3. 切换到 Network 标签",
            "4. 刷新页面，找到请求头中的 Cookie",
            "5. 复制完整的 Cookie 值"
        ]
    },
    "wordpress": {
        "name": "WordPress",
        "icon": "📝",
        "description": "发布文章到WordPress站点",
        "docs_url": "https://developer.wordpress.org/rest-api/",
        "required_configs": ["wordpress_url", "wordpress_username", "wordpress_password"],
        "setup_steps": [
            "1. 确保WordPress站点已启用REST API",
            "2. 登录WordPress后台",
            "3. 进入 用户 > 应用密码",
            "4. 创建新的应用密码",
            "5. 使用用户名和应用密码配置"
        ]
    }
}

@router.get("/dashboard")
async def get_dashboard_data(db: AsyncSession = Depends(get_db)):
    """获取仪表盘数据"""
    # 获取热点源数量
    result = await db.execute(select(HotspotSource))
    hotspot_sources_count = len(result.scalars().all())
    
    # 获取内容任务统计
    result = await db.execute(select(ContentTask))
    content_tasks_count = len(result.scalars().all())
    
    result = await db.execute(select(ContentTask).filter(ContentTask.status == "completed"))
    completed_tasks_count = len(result.scalars().all())
    
    # 获取发布记录统计
    result = await db.execute(select(PublishRecord))
    publish_records_count = len(result.scalars().all())
    
    result = await db.execute(select(PublishRecord).filter(PublishRecord.status == "published"))
    published_count = len(result.scalars().all())
    
    return {
        "hotspot_sources": hotspot_sources_count,
        "content_tasks": {
            "total": content_tasks_count,
            "completed": completed_tasks_count
        },
        "publish_records": {
            "total": publish_records_count,
            "published": published_count
        }
    }

@router.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    return {
        "event_bus": "connected",
        "task_queue": "connected",
        "database": "connected"
    }

@router.post("/system/config")
async def update_system_config(config_data: Dict[str, Any]):
    """更新系统配置"""
    # 发布配置更新事件
    await event_bus.publish("system", "config_updated", config_data)
    
    return {"message": "配置已更新"}

@router.get("/logs")
async def get_system_logs(log_type: str = "system", limit: int = 100):
    """获取系统日志"""
    # 这里应该从日志文件或数据库读取日志
    # 简化实现，返回示例数据
    return {
        "logs": [
            {"timestamp": "2026-06-22 10:00:00", "level": "INFO", "message": "系统启动"},
            {"timestamp": "2026-06-22 10:01:00", "level": "INFO", "message": "热点监控开始"}
        ]
    }

@router.get("/configs", response_model=List[Dict[str, Any]])
async def get_all_configs(category: str = None, platform: str = None, db: AsyncSession = Depends(get_db)):
    """获取所有配置"""
    query = select(SystemConfig)
    if category:
        query = query.filter(SystemConfig.category == category)
    if platform:
        query = query.filter(SystemConfig.platform == platform)
    result = await db.execute(query)
    configs = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "key": c.key,
            "value": "***" if c.is_sensitive and c.value else c.value,
            "description": c.description,
            "help": c.help,
            "category": c.category,
            "platform": c.platform,
            "is_sensitive": c.is_sensitive
        }
        for c in configs
    ]

@router.get("/configs/{key}")
async def get_config(key: str, db: AsyncSession = Depends(get_db)):
    """获取单个配置"""
    result = await db.execute(select(SystemConfig).filter(SystemConfig.key == key))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return {
        "id": config.id,
        "key": config.key,
        "value": config.value,
        "description": config.description,
        "help": config.help,
        "category": config.category,
        "platform": config.platform,
        "is_sensitive": config.is_sensitive
    }

@router.put("/configs/{key}")
async def update_config(key: str, config_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """更新配置"""
    result = await db.execute(select(SystemConfig).filter(SystemConfig.key == key))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    config.value = config_data.get("value", config.value)
    await db.commit()
    
    # 发布配置更新事件
    await event_bus.publish("system", "config_updated", {"key": key, "value": config.value})
    
    return {"message": "配置已更新", "key": key}

@router.post("/configs/init")
async def init_default_configs(db: AsyncSession = Depends(get_db)):
    """初始化默认配置"""
    for config_data in DEFAULT_CONFIGS:
        result = await db.execute(select(SystemConfig).filter(SystemConfig.key == config_data["key"]))
        existing = result.scalar_one_or_none()
        if not existing:
            config = SystemConfig(**config_data)
            db.add(config)
    
    await db.commit()
    return {"message": f"已初始化 {len(DEFAULT_CONFIGS)} 个默认配置"}

@router.get("/platforms/info")
async def get_platforms_info():
    """获取所有平台配置信息"""
    return PLATFORM_INFO

@router.get("/platforms/info/{platform_type}")
async def get_platform_info(platform_type: str):
    """获取指定平台配置信息"""
    if platform_type not in PLATFORM_INFO:
        raise HTTPException(status_code=404, detail="平台不存在")
    return PLATFORM_INFO[platform_type]