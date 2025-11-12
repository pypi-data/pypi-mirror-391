import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Union

@dataclass
class Edge:
    """dataclass representing edges"""
    start: Union[str, int]
    end: Union[str, int]
    id: Union[str, int] = field(default_factory=lambda: str(uuid.uuid4()))
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.start, (str, int)):
            raise TypeError(f"'start' must be a string or int (got {type(self.start).__name__})")
        if not isinstance(self.end, (str, int)):
            raise TypeError(f"'end' must be a string or int (got {type(self.end).__name__})")
        if not isinstance(self.properties, dict):
            raise TypeError(f"'properties' must be a dict (got {type(self.properties).__name__})")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        """
        Create an Edge from a dict. Unknown keys are ignored.
        """
        return cls(
            start=data["start"],
            end=data["end"],
            properties=data.get("properties", {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Edge back to a plain dict.

        This does not use `asdict` by design, because the mappings add more fields
        to this instance which would be transferred by `asdict`.
        """
        return dict(self.__dict__)

    def __getitem__(self, key: str) -> Any:
        """Enable edge['start'] and edge['properties'] access."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key!r} is not a valid field of Node")

    def __setitem__(self, key: str, value: Any) -> None:
        """Allow assignment like edge['start'] = ..., and arbitrary keys."""
        setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Mimic dict.get(key, default)."""
        return getattr(self, key, default)