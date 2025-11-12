from dataclasses import dataclass
from enum import Enum
from typing import Dict, Union, Any

class DashStyle(str, Enum):
    SOLID="solid"
    DASH="dash"
    DOT="dot"
    DASH_DOT="dash-dot"
    DASH_DOT_DOT="dash-dot-dot"

@dataclass
class EdgeStyle:
    """dataclass to style edges"""
    color: Union[str, None] = None
    directed: Union[bool, None] = None
    thickness: Union[float, None] = None
    dash_style: Union[DashStyle, str, None] = None

    def to_js(self) -> Dict[str, Any]:
        """Send JS-ified keys to the web frontend"""
        d: Dict[str, Any] = {}
        if self.color:
            d["color"] = self.color
        if self.directed:
            d["directed"] = self.directed
        if self.thickness:
            d["thickness"] = self.thickness
        if self.dash_style:
            if isinstance(self.dash_style, DashStyle):
                d["dashStyle"] = self.dash_style.value
            else:
                d["dashStyle"] = self.dash_style
        return d