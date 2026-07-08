from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PARAKH_", env_file=".env", extra="ignore")

    # Accepts the conventional DATABASE_URL as well as PARAKH_DATABASE_URL.
    database_url: str = Field(
        "postgres://postgres:postgres@localhost:5432/parakh",
        validation_alias=AliasChoices("PARAKH_DATABASE_URL", "DATABASE_URL"),
    )

    # Ingestion cadence (design: cron every 10 min).
    fetch_interval_minutes: int = 10

    # Clustering knobs — tuned by the bilingual spike (docs/M1-embedding-spike.md).
    # Set "hash" to select the deterministic non-semantic embedder (tests/dev).
    embedding_model: str = "intfloat/multilingual-e5-large"  # or BAAI/bge-m3
    # Tuned on REAL ingested data (docs/M1-precision.md § Real data): max-F1 among
    # gate-passing thresholds. precision 0.979, recall 0.575, F1 0.724 @ 0.86.
    # (The authored bootstrap set wanted 0.88; real multi-outlet coverage is phrased
    # more alike, so the operating point is lower. Recall/fragmentation is the real gap.)
    cluster_sim_threshold: float = 0.86
    cluster_window_hours: int = 72

    # Bias-bar / blindspot gates (design rules).
    min_rated_for_distribution: int = 5
    blindspot_min_rated: int = 5
    blindspot_low_share: float = 0.20
    blindspot_high_share: float = 0.60


settings = Settings()
