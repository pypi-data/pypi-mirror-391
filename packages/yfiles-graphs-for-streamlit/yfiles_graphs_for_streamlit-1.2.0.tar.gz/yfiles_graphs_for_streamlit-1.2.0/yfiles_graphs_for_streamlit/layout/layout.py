from enum import Enum

class Layout(str, Enum):
    """Automatic layout algorithms"""
    CIRCULAR = "circular"
    CIRCULAR_STRAIGHT_LINE = "circular_straight_line"
    HIERARCHIC = "hierarchic"
    ORGANIC = "organic"
    INTERACTIVE_ORGANIC = "interactive_organic"
    ORTHOGONAL = "orthogonal"
    RADIAL = "radial"
    TREE = "tree"
    MAP = "map"
    ORTHOGONAL_EDGE_ROUTER = "orthogonal_edge_router"
    ORGANIC_EDGE_ROUTER = "organic_edge_router"
    NO_LAYOUT = "no_layout"