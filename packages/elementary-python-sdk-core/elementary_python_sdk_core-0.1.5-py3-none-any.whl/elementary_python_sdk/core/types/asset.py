from typing import Literal

from elementary_python_sdk.core.logger import get_logger
from elementary_python_sdk.core.types.base import ElementaryVersionedModel

logger = get_logger()


class Asset(ElementaryVersionedModel):
    name: str
    description: str
    owners: list[str]
    tags: list[str]

    @property
    def id(self) -> str:
        return f"asset.{self.name}"


class TableAsset(Asset):
    kind: Literal["table_asset"] = "table_asset"
    fqn: str
