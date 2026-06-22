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
        extra = "ignore"  # 忽略额外的环境变量

def load_platform_config(platform_name: str) -> Dict:
    """加载平台配置"""
    config_path = Path("config/platforms.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config.get(platform_name, {})
    return {}

settings = Settings()

# 数据库配置缓存
_db_configs: Dict[str, str] = {}

async def load_configs_from_db():
    """从数据库加载配置"""
    global _db_configs
    from .database import get_db
    from .models.config import SystemConfig
    
    try:
        async for db in get_db():
            configs = await db.query(SystemConfig).all()
            _db_configs = {c.key: c.value for c in configs}
            break
    except Exception as e:
        print(f"从数据库加载配置失败: {e}")

def get_config(key: str, default: str = "") -> str:
    """获取配置值，优先从数据库读取"""
    return _db_configs.get(key, default)

def get_llm_config(provider: str) -> Dict:
    """获取LLM配置"""
    if provider == "openai":
        return {
            "api_key": get_config("openai_api_key", settings.llm_providers["openai"]["api_key"]),
            "model": get_config("openai_model", settings.llm_providers["openai"]["model"]),
            "max_tokens": int(get_config("openai_max_tokens", str(settings.llm_providers["openai"]["max_tokens"])))
        }
    elif provider == "claude":
        return {
            "api_key": get_config("claude_api_key", settings.llm_providers["claude"]["api_key"]),
            "model": get_config("claude_model", settings.llm_providers["claude"]["model"]),
            "max_tokens": int(get_config("claude_max_tokens", str(settings.llm_providers["claude"]["max_tokens"])))
        }
    return {}

def get_platform_config(platform_name: str) -> Dict:
    """获取平台配置"""
    if platform_name == "wechat":
        return {
            "app_id": get_config("wechat_app_id"),
            "app_secret": get_config("wechat_app_secret")
        }
    elif platform_name == "weibo":
        return {
            "access_token": get_config("weibo_access_token")
        }
    elif platform_name == "zhihu":
        return {
            "client_id": get_config("zhihu_client_id"),
            "client_secret": get_config("zhihu_client_secret")
        }
    elif platform_name == "xiaohongshu":
        return {
            "cookie": get_config("xiaohongshu_cookie")
        }
    elif platform_name == "wordpress":
        return {
            "url": get_config("wordpress_url"),
            "username": get_config("wordpress_username"),
            "password": get_config("wordpress_password")
        }
    return load_platform_config(platform_name)