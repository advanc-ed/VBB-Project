import os
from dataclasses import MISSING, dataclass, fields

import toml


@dataclass
class ConfigBot:
    token: str


@dataclass
class ConfigSettings:
    owner_id: int
    throttling_rate: float = 0.5
    drop_pending_updates: bool = True


@dataclass
class ConfigDb:
    database_url: str = os.getenv('DATABASE_URL')


@dataclass
class ConfigApi:
    id: int = 2040
    hash: str = "b18441a1ff607e10a989891a5462e627"
    bot_api_url: str = "https://api.telegram.org"

    @property
    def is_local(self):
        return self.bot_api_url != "https://api.telegram.org"


@dataclass
class Config:
    bot: ConfigBot
    settings: ConfigSettings
    db: ConfigDb
    api: ConfigApi

    @classmethod
    def parse(cls, data: dict) -> "Config":
        sections = {}

        for section in fields(cls):
            pre = {}
            current = data[section.name]

            for field in fields(section.type):
                if field.name in current:
                    pre[field.name] = current[field.name]
                elif field.default is not MISSING:
                    pre[field.name] = field.default
                else:
                    raise ValueError(
                        "Missing field %s in section %s" % (
                            field.name, section.name)
                    )

            sections[section.name] = section.type(**pre)

        return cls(**sections)


def parse_config(config_file: str):
    if not os.path.isfile(config_file) and not config_file.endswith('.toml'):
        config_file += ".toml"

    if not os.path.isfile(config_file):
        raise FileNotFoundError(
            "Config file not found: %s no such file." % config_file
        )

    with open(config_file, "r") as f:
        data = toml.load(f)

    return Config.parse(dict(data))
