from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    cors_origins: str = "*"
    database_url: str = "mysql+asyncmy://root:password@127.0.0.1:3306/w_ai_learn?charset=utf8mb4"
    database_echo: bool = False
    session_file_path: str = "./data/sessions.json"
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    wechat_mock_login: bool = False
    jwt_secret: str = "change_me_in_production"
    jwt_expire_days: int = 7
    min_source_text_length: int = 5
    max_source_text_length: int = 2000
    min_question_count: int = 5
    max_question_count: int = 10
    llm_max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
