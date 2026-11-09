"""Fail-closed Unity Catalog names; no credential or workspace defaults."""
from dataclasses import dataclass
import re


def identifier(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", value):
        raise ValueError(f"Invalid Unity Catalog identifier: {value!r}")
    return value


@dataclass(frozen=True)
class LakehouseConfig:
    catalog: str
    prefix: str = "sp500"

    def __post_init__(self):
        identifier(self.catalog)
        identifier(self.prefix)

    def schema(self, layer: str) -> str:
        if layer not in {"files", "bronze", "silver", "gold", "ops"}:
            raise ValueError("Unknown layer")
        return f"{self.catalog}.{identifier(self.prefix + '_' + layer)}"

    def table(self, layer: str, entity: str) -> str:
        return f"{self.schema(layer)}.{identifier(entity)}"

    def volume(self, name: str) -> str:
        if name not in {"landing", "checkpoints", "exports"}:
            raise ValueError("Unknown volume")
        return f"/Volumes/{self.catalog}/{self.prefix}_files/{name}"

    def require_landing_path(self, path: str) -> str:
        return self.require_volume_path('landing',path)

    def require_volume_path(self, name: str, path: str) -> str:
        root = self.volume(name) + "/"
        if not path.startswith(root) or any(p in {"..", "."} for p in path.split("/")):
            raise ValueError("Input must be under the configured " + name + " volume")
        return path
