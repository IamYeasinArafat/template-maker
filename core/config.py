from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    TEMPLATE_PATH: Path = PROJECT_ROOT / "template"
    ASSETS_PATH: Path = PROJECT_ROOT / "assets"