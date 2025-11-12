from dataclasses import dataclass
from enum import Enum
from typing import Dict, Union

class NodeShape(str, Enum):
    ELLIPSE="ellipse"
    HEXAGON="hexagon"
    HEXAGON2="hexagon2"
    OCTAGON="octagon"
    PILL="pill"
    RECTANGLE="rectangle"
    ROUND_RECTANGLE="round-rectangle"
    TRIANGLE="triangle"

@dataclass
class NodeStyle:
    """dataclass to style nodes"""
    color: Union[str, None] = None
    image: Union[str, None] = None
    shape: Union[NodeShape, None] = None

    def to_js(self) -> Dict:
        """Send JS-ified keys to the web frontend"""
        d = {}
        if self.color:
            d["color"] = self.color
        if self.image:
            d["image"] = self.image
        if self.shape:
            d["shape"] = self.shape.value
        return d