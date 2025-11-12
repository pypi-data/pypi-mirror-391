# xbyter_common/sets/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv  # ✅ 关键：显式加载 .env 文件


class Settings(BaseSettings):
    """
    全局配置类
    """
    APP_NAME: str = "DefaultApp"
    ENVIRONMENT: str = "dev"  # 环境变量控制加载哪个配置文件
    APP_PORT:int = 8080
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"

    # 自动选择 .env 文件
    model_config = SettingsConfigDict(
        env_file=None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @classmethod
    def load(cls):
        """
        根据 ENVIRONMENT 自动加载对应的 .env 文件
        """
        # 优先从环境变量读取 ENVIRONMENT
        environment = os.getenv("ENVIRONMENT", "dev")
        base_dir = Path(__file__).resolve().parent.parent.parent / "ai_api"

        env_file_path = base_dir / f".env.{environment}"
        if not env_file_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {env_file_path}")

        # ✅ 关键步骤：先手动载入所有 .env 变量到系统环境中
        load_dotenv(env_file_path, override=True)

        # 动态加载
        cls.model_config["env_file"] = str(env_file_path)

        print(f"✅ 当前环境: {environment}, 使用配置文件: {env_file_path}")
        return cls()

    def get(self, key: str) -> str:
        """
        根据配置项名称获取值，若不存在则返回空字符串
        支持读取：
          1. Settings 类中定义的字段
          2. 环境变量中动态存在的字段
        """
        # 优先从当前实例属性中取
        if hasattr(self, key):
            return str(getattr(self, key))

        # 再从环境变量中取
        return os.getenv(key, "")

# 提供一个全局可用实例（懒加载）
settings = Settings.load()