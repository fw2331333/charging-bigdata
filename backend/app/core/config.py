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

    # 机器学习模型目录（train_all_models.py 产出）
    ANALYTICS_OUTPUT_DIR: str = "../analytics/output"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
