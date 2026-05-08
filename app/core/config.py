from dataclasses import dataclass
from pathlib import Path
import os
import sys

from dotenv import load_dotenv


SOURCE_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", SOURCE_ROOT))
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else SOURCE_ROOT
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(APP_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Loop Adventure")
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(DATA_DIR / 'os_transport.db').as_posix()}",
    )
    root_dir: Path = APP_DIR
    resource_dir: Path = RESOURCE_DIR
    data_dir: Path = DATA_DIR
    output_pdf_dir: Path = Path.home() / "Downloads"
    logo_path: Path = RESOURCE_DIR / "logoloop.png"
    icon_path: Path = RESOURCE_DIR / "loop_adventure.ico"


settings = Settings()
