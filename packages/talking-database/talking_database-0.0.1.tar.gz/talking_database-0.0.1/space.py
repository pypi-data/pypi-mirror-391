from typing import Optional
from dataclasses import dataclass


from sqlalchemy import Engine
from pydantic import BaseModel, Field


class SpaceConfig:
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)


@dataclass
class Space:
    config: SpaceConfig
    engine: Engine

    @property
    def name(self) -> str:
        return self.config.name or self.engine.url.database

    @property
    def description(self) -> str:
        return self.config.description or ""
