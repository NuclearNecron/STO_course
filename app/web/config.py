import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from .app import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass
class GRPCConfig:
    host: str
    port: int


@dataclass
class Config:
    database: DatabaseConfig = None
    session: SessionConfig | None = None
    grpc: GRPCConfig | None = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)
    app.config = Config(
        session=SessionConfig(
            key=raw_config["session"]["key"],
        ),
        database=DatabaseConfig(**raw_config["database"]),
        grpc=GRPCConfig(
            host=raw_config["grpc"]["host"], port=raw_config["grpc"]["port"]
        ),
    )
