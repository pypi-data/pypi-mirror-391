from abc import ABC
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T", bound="ModelEntity")


class ModelEntity(BaseModel, ABC):
    id: str | int | UUID | None = None

    class Config:
        arbitrary_types_allowed = True
