import json
from pathlib import Path
from typing import Any, Dict

from spotkit.exceptions import SpotKitConfigError

CONFIG_DIR = Path.home() / ".spotkit"
CONFIG_FILE = CONFIG_DIR / "config.json"

CONFIG_VALUES: Dict[str, Any] = {
    "spotify_client_id": "",
    "spotify_client_secret": "",
    "spotify_redirect_uri": "",
}


class Config:
    """Simple local configuration manager for SpotKit."""

    def __init__(self) -> None:
        self.data = CONFIG_VALUES.copy()
        self._load()

    def _load(self) -> None:
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    user_data = json.load(f)
                self.data.update(user_data)
            else:
                self.save()  # create if missing
        except json.JSONDecodeError as e:
            raise SpotKitConfigError(details=f"Invalid JSON in config file: {e}")
        except OSError as e:
            raise SpotKitConfigError(details=f"Failed to read config file: {e}")

    def save(self) -> None:
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except OSError as e:
            raise SpotKitConfigError(details=f"Failed to save config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        try:
            self.save()
        except SpotKitConfigError:
            raise


# Shortcut helpers
def load_config() -> Config:
    return Config()
