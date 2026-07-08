"""应用配置：从环境变量读取，便于多环境部署。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "新能源充电桩大数据分析系统"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # HDFS WebHDFS（与 analytics 模块一致）
    HDFS_NN_HOST: str = "http://hadoop-master:9870"
    HDFS_USER: str = "hadoop"

    # MySQL（MapReduce 结果、BI 同源）
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "charging_bigdata"

    # JWT（双 Token：短期 Access + 长期 Refresh）
    JWT_SECRET: str = "charging-bigdata-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # 机器学习模型目录（train_all_models.py 产出）
    ANALYTICS_OUTPUT_DIR: str = "../analytics/output"

    # 智能助手（DeepSeek / OpenAI 兼容 + RAG）
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"
    LLM_TIMEOUT_SECONDS: int = 90
    RAG_TOP_K: int = 4
    RAG_USE_VECTOR: bool = True
    RAG_CHROMA_DIR: str = "chroma_db"
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
    RAG_INSECURE_SSL: bool = False

    # ETL 完成后通知后端清 BI 缓存（与 pipeline.env 中 PIPELINE_SECRET 一致）
    PIPELINE_SECRET: str = "charging-pipeline-dev"
    BACKEND_URL: str = "http://127.0.0.1:8000"

    # 邮箱注册 / 忘记密码（邮件链接设密，见 .env.example 说明）
    APP_PUBLIC_URL: str = "http://127.0.0.1:5173"
    EMAIL_VERIFY_EXPIRE_HOURS: int = 24
    PROFILE_OTP_EXPIRE_MINUTES: int = 10

    # SMTP（SMTP_HOST + SMTP_USER 均非空时启用发信）
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587  # 587=STARTTLS，465=SSL
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""  # QQ 邮箱填 SMTP 授权码
    SMTP_FROM: str = "Charging Big Data <noreply@example.com>"
    SMTP_USE_TLS: bool = True

    @property
    def smtp_configured(self) -> bool:
        return bool(self.SMTP_HOST.strip() and self.SMTP_USER.strip())

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
