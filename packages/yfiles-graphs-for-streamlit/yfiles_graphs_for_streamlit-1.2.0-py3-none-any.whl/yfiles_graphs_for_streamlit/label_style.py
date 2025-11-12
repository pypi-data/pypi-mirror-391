from dataclasses import dataclass
from enum import Enum
from typing import Dict, Union, Any


class LabelPosition(str, Enum):
    CENTER="center"
    NORTH="north"
    EAST="east"
    SOUTH="south"
    WEST="west"

class TextWrapping(str, Enum):
    NONE="none"
    CHARACTER="character"
    CHARACTER_ELLIPSIS="character_ellipsis"
    WORD="word"
    WORD_ELLIPSIS="word_ellipsis"

class FontWeight(str, Enum):
    BOLD='bold'
    BOLDER='bolder'
    NORMAL='normal'
    LIGHTER='lighter'

class TextAlignment(str, Enum):
    CENTER='center'
    LEFT='left'
    RIGHT='right'

@dataclass
class LabelStyle:
    """dataclass to style labels"""
    text: Union[str, None] = None
    font_size: Union[int, None] = None
    font_weight: Union[FontWeight, None] = None
    color: Union[str, None] = None
    background_color: Union[str, None] = None
    position: Union[LabelPosition, None] = None
    maximum_width: Union[int, None] = None
    maximum_height: Union[int, None] = None
    wrapping: Union[TextWrapping, None] = None
    text_alignment: Union[TextAlignment, None] = None

    def to_js(self) -> Dict[str, Any]:
        """Send JS-ified keys to the web frontend"""
        d: Dict[str, Any] = {}
        if self.text:
            d["text"] = self.text
        if self.font_size:
            d["fontSize"] = self.font_size
        if self.font_weight:
            d["fontWeight"] = self.font_weight.value
        if self.color:
            d["color"] = self.color
        if self.background_color:
            d["backgroundColor"] = self.background_color
        if self.position:
            d["position"] = self.position.value
        if self.maximum_width:
            d["maximumWidth"] = self.maximum_width
        if self.maximum_height:
            d["maximumHeight"] = self.maximum_height
        if self.wrapping:
            d["wrapping"] = self.wrapping.value
        if self.text_alignment:
            d["textAlignment"] = self.text_alignment.value
        return d