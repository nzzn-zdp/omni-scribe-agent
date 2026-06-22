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