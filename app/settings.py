import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


@dataclass(frozen=True)
class Settings:
    telemetry_api_key: str | None
    database_url: str


settings = Settings(
    telemetry_api_key=os.getenv("TELEMETRY_API_KEY"),
    database_url=os.getenv(
        "DATABASE_URL",
        "sqlite:///./telemetry.db",
    ),
)
