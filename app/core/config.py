from dataclasses import dataclass

import yaml

import typing
if typing.TYPE_CHECKING:
    from app.core.application import Application


@dataclass
class RedisConfig:
    host: str | None = None
    port: int | None = None
    db: int | None = None


@dataclass
class Config:
    redis: RedisConfig | None = None


def setup_config(app: 'Application', config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(
        redis=RedisConfig(
            host=raw_config["redis"]["host"],
            port=raw_config["redis"]["port"],
            db=raw_config["redis"]["db"]
        )
    )
