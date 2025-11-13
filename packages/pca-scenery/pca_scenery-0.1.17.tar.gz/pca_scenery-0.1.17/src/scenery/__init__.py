"""A versatile integration testing framework for web apps."""
import configparser
import logging
from typing import Any

from rich.console import Console

class SceneryLogger:

    style_map = {
        logging.DEBUG: None,
        logging.INFO: "blue",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
    }

    def __init__(self, level: int):
        self.level = level
        self.console = console
        # pass

    def log(self, level: int, msg: Any, style: str | None = None) -> None:
        if self.level <= level:
            level_name = f"{logging.getLevelName(level)}"
            level_name = f"{level_name:<10}"
            color = self.style_map[level]
            if color:
                level_name = f"[{color}]{level_name}[/{color}]"
                msg = level_name + str(msg)
            self.console.log(msg, style=style)

    def info(self, msg: Any, style: str | None =None) -> None:
        self.log(logging.INFO, msg, style)

    def debug(self, msg: Any, style: str | None =None) -> None:
        self.log(logging.DEBUG, msg, style)

    def warning(self, msg: Any, style: str | None =None) -> None:
        self.log(logging.WARNING, msg, style)

    def error(self, msg: Any, style: str | None =None) -> None:
        self.log(logging.ERROR, msg, style)


class SceneryConfig(configparser.ConfigParser):

    @property
    def framework(self):
        if self.has_section("app"):
            return self.get("app", "framework")
        else:
            return None
    
    @property
    def manifests_folder(self):
        return self.get("manifests", "folder")
    
    @property
    def common_items(self):
        return self.get("manifests", "common", fallback=None)

    @property
    def selenium_instructions(self):
        if self.has_section("instructions"):
            return self.get("instructions", "selenium", fallback=None)
        else:
            return None
    
    @property
    def setup_instructions(self):
        if self.has_section("instructions"):
            return self.get("instructions", "setup", fallback=None)
        else:
            return None
    
    @property
    def django_app_name(self):
        return self.get("app-django", "name")
    
    @property
    def urls(self):
        return self["urls"]

console = Console()
logger = SceneryLogger(logging.INFO)
config = SceneryConfig()


