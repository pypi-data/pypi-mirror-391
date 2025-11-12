import os
import sys
from pathlib import Path
from typing import TypedDict, cast
from contextlib import contextmanager
import tomlkit

from zet.entities import Stop

ZET_CONFIG_DIR_NAME = "zet"
ZET_SETTINGS_FILE_NAME = "settings.toml"
ZET_STYLESHEET_FILE_NAME = "styles.tcss"


class Config(TypedDict):
    favourite_stops: list[str]


def get_config_dir() -> Path:
    """Returns the path to zet config directory"""

    # On Windows, store the config in roaming appdata
    if sys.platform == "win32" and "APPDATA" in os.environ:
        return Path(os.getenv("APPDATA")) / ZET_CONFIG_DIR_NAME

    # Respect XDG_CONFIG_HOME env variable if set
    # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    if "XDG_CONFIG_HOME" in os.environ:
        config_home = Path(os.environ["XDG_CONFIG_HOME"]).expanduser()
        return config_home / ZET_CONFIG_DIR_NAME

    # Default to ~/.config/zet/
    return Path.home() / ".config" / ZET_CONFIG_DIR_NAME


def get_settings_path() -> Path:
    return get_config_dir() / ZET_SETTINGS_FILE_NAME


def get_stylesheet_path() -> Path:
    return get_config_dir() / ZET_STYLESHEET_FILE_NAME


def empty_config() -> Config:
    return {
        "favourite_stops": [],
    }


def load_config() -> Config:
    path = get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        with path.open("r") as f:
            config = tomlkit.load(f)
            return cast(Config, config)
    else:
        return empty_config()


def save_config(config: Config):
    path = get_settings_path()
    with path.open("w") as f:
        tomlkit.dump(config, f)


@contextmanager
def edit_config():
    config = load_config()
    try:
        yield config
    finally:
        save_config(config)


def add_favourite_stop(stop: Stop):
    with edit_config() as config:
        favourite_stops = config.get("favourite_stops", [])
        favourite_stops.append(stop["id"])
        config["favourite_stops"] = list(set(favourite_stops))


def remove_favourite_stop(stop: Stop):
    with edit_config() as config:
        favourite_stops = config.get("favourite_stops", [])
        favourite_stops = [s for s in favourite_stops if s != stop["id"]]
        config["favourite_stops"] = favourite_stops
