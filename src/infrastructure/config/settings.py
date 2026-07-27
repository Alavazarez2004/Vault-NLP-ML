from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    data_dir: Path = Path("data/generated")
    real_data_dir: Path = Path("data/real")
    models_dir: Path = Path("models")

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_anon_key: str = ""
    database_url: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    n_synthetic_users: int = 1000
    random_seed: int = 42

    api_host: str = "0.0.0.0"
    api_port: int = 8006
    api_prefix: str = "/api/v1"

    rabbitmq_url: str = "amqp://guest:guest@localhost/"
    rabbitmq_exchange: str = "vault.events"
    rabbitmq_consume_queue: str = "vault-ai-service.events"
    rabbitmq_consume_routing_keys: list[str] = [
        "post.created",
        "comment.created",
        "review.created",
        "asset.updated",
    ]
    rabbitmq_publish_routing_key: str = "nlp.analyzed"

    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
