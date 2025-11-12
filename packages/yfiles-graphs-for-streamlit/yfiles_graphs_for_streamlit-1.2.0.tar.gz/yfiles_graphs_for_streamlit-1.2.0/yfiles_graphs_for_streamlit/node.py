from dataclasses import dataclass, field
from typing import Any, Dict, Union

@dataclass
class Node:
    """dataclass representing nodes"""
    id: Union[str, int]
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.id, (str, int)):
            raise TypeError(f"'id' must be a string or int (got {type(self.id).__name__})")
        if not isinstance(self.properties, dict):
            raise TypeError(f"'properties' must be a dict (got {type(self.properties).__name__})")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        """
        Create a Node from a dict. Unknown keys are ignored.
        """
        return cls(
            id=data["id"],
            properties=data.get("properties", {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Node back to a plain dict.

        This does not use `asdict` by design, because the mappings add more fields
        to this instance which would be transferred by `asdict`.
        """
        return dict(self.__dict__)

    def __getitem__(self, key: str) -> Any:
        """Enable node['id'] and node['properties'] access."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key!r} is not a valid field of Node")

    def __setitem__(self, key: str, value: Any) -> None:
        """Allow assignment like node['id'] = ..., and arbitrary keys."""
        setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Mimic dict.get(key, default)."""
        return getattr(self, key, default)