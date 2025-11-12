"""Configuration handling for Esprit."""

from dataclasses import dataclass
from pathlib import Path

import tomllib

CONFIG_PATH = Path.home() / ".config" / "esprit" / "config.toml"


@dataclass(slots=True)
class EspritConfig:
    """Runtime configuration for the Esprit application."""

    theme: str = "tokyo-night"


def load_config() -> EspritConfig:
    # if no config, return default
    if not CONFIG_PATH.exists():
        return EspritConfig()

    try:
        with CONFIG_PATH.open("rb") as config_file:
            raw_config = tomllib.load(config_file)
    except (OSError, tomllib.TOMLDecodeError) as e:
        print(f"Error reading config: {e}")
        print("Using defaults")
        return EspritConfig()

    config = EspritConfig()
    # TODO: validate theme values
    config.theme = str(raw_config.get("theme", "tokyo-night")).strip().lower()

    return config
