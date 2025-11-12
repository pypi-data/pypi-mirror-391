import os
from typing import Callable, Dict, List, Optional, Tuple
import streamlit.components.v1 as components
from .widget import GraphWidget
from .data_sanitizer import make_json_safe

# re-exports
from .label_style import *
from .layout.layout import *
from .node_style import *
from .edge_style import *
from .node import *
from .edge import *

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component("Streamlit_Graph_Widget", url='http://localhost:5173')
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _component_func = components.declare_component("Streamlit_Graph_Widget", path=build_dir)

class StreamlitGraphWidget(GraphWidget):
    def __init__(self,
                 nodes: Optional[List[Union[Node, Dict[str, Any]]]] = None,
                 edges: Optional[List[Union[Edge, Dict[str, Any]]]] = None,
                 heat_mapping: Optional[Union[str, Callable[[dict], float]]] = None,
                 node_label_mapping: Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]] = None,
                 node_property_mapping: Optional[Union[str, Callable[[dict], dict]]] = None,
                 node_color_mapping: Optional[Union[str, Callable[[dict], str]]] = None,
                 node_styles_mapping: Optional[Union[str, Callable[[dict], NodeStyle]]] = None,
                 node_scale_factor_mapping: Optional[Union[str, Callable[[dict], float]]] = None,
                 node_size_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]] = None,
                 node_layout_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float, float, float]]]] = None,
                 node_cell_mapping: Optional[Union[str, Callable[[dict], Tuple[int, int]]]] = None,
                 node_type_mapping: Optional[Union[str, Callable[[dict], str]]] = None,
                 node_parent_mapping: Optional[Union[str, Callable[[dict], Union[str, int, float]]]] = None,
                 node_position_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]] = None,
                 node_coordinate_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]] = None,
                 node_parent_group_mapping: Optional[Union[str, Callable[[dict], Union[str, dict]]]] = None,
                 edge_label_mapping: Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]] = None,
                 edge_property_mapping: Optional[Union[str, Callable[[dict], dict]]] = None,
                 edge_color_mapping: Optional[Union[str, Callable[[dict], str]]] = None,
                 edge_styles_mapping: Optional[Union[str, Callable[[dict], EdgeStyle]]] = None,
                 edge_thickness_factor_mapping: Optional[Union[str, Callable[[dict], float]]] = None,
                 directed_mapping: Optional[Union[str, Callable[[dict], bool]]] = None):
        super().__init__()
        # Preserve previous behavior: only set nodes/edges if both are provided
        if nodes is not None and edges is not None:
            self.nodes = nodes
            self.edges = edges

        # Set optional properties if provided
        if heat_mapping is not None:
            self.heat_mapping = heat_mapping
        if node_label_mapping is not None:
            self.node_label_mapping = node_label_mapping
        if node_property_mapping is not None:
            self.node_property_mapping = node_property_mapping
        if node_color_mapping is not None:
            self.node_color_mapping = node_color_mapping
        if node_styles_mapping is not None:
            self.node_styles_mapping = node_styles_mapping
        if node_scale_factor_mapping is not None:
            self.node_scale_factor_mapping = node_scale_factor_mapping
        if node_size_mapping is not None:
            self.node_size_mapping = node_size_mapping
        if node_layout_mapping is not None:
            self.node_layout_mapping = node_layout_mapping
        if node_cell_mapping is not None:
            self.node_cell_mapping = node_cell_mapping
        if node_type_mapping is not None:
            self.node_type_mapping = node_type_mapping
        if node_parent_mapping is not None:
            self.node_parent_mapping = node_parent_mapping
        if node_position_mapping is not None:
            self.node_position_mapping = node_position_mapping
        if node_coordinate_mapping is not None:
            self.node_coordinate_mapping = node_coordinate_mapping
        if node_parent_group_mapping is not None:
            self.node_parent_group_mapping = node_parent_group_mapping
        if edge_label_mapping is not None:
            self.edge_label_mapping = edge_label_mapping
        if edge_property_mapping is not None:
            self.edge_property_mapping = edge_property_mapping
        if edge_color_mapping is not None:
            self.edge_color_mapping = edge_color_mapping
        if edge_styles_mapping is not None:
            self.edge_styles_mapping = edge_styles_mapping
        if edge_thickness_factor_mapping is not None:
            self.edge_thickness_factor_mapping = edge_thickness_factor_mapping
        if directed_mapping is not None:
            self.directed_mapping = directed_mapping

    @classmethod
    def from_graph(cls,
                   graph: Any,
                   heat_mapping: Optional[Union[str, Callable[[dict], float]]] = None,
                   node_label_mapping: Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]] = None,
                   node_property_mapping: Optional[Union[str, Callable[[dict], dict]]] = None,
                   node_color_mapping: Optional[Union[str, Callable[[dict], str]]] = None,
                   node_styles_mapping: Optional[Union[str, Callable[[dict], NodeStyle]]] = None,
                   node_scale_factor_mapping: Optional[Union[str, Callable[[dict], float]]] = None,
                   node_size_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]] = None,
                   node_layout_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float, float, float]]]] = None,
                   node_cell_mapping: Optional[Union[str, Callable[[dict], Tuple[int, int]]]] = None,
                   node_type_mapping: Optional[Union[str, Callable[[dict], str]]] = None,
                   node_parent_mapping: Optional[Union[str, Callable[[dict], Union[str, int, float]]]] = None,
                   node_position_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]] = None,
                   node_coordinate_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]] = None,
                   node_parent_group_mapping: Optional[Union[str, Callable[[dict], Union[str, dict]]]] = None,
                   edge_label_mapping: Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]] = None,
                   edge_property_mapping: Optional[Union[str, Callable[[dict], dict]]] = None,
                   edge_color_mapping: Optional[Union[str, Callable[[dict], str]]] = None,
                   edge_styles_mapping: Optional[Union[str, Callable[[dict], EdgeStyle]]] = None,
                   edge_thickness_factor_mapping: Optional[Union[str, Callable[[dict], float]]] = None,
                   directed_mapping: Optional[Union[str, Callable[[dict], bool]]] = None):
        instance = cls(
            heat_mapping=heat_mapping,
            node_label_mapping=node_label_mapping,
            node_property_mapping=node_property_mapping,
            node_color_mapping=node_color_mapping,
            node_styles_mapping=node_styles_mapping,
            node_scale_factor_mapping=node_scale_factor_mapping,
            node_size_mapping=node_size_mapping,
            node_layout_mapping=node_layout_mapping,
            node_cell_mapping=node_cell_mapping,
            node_type_mapping=node_type_mapping,
            node_parent_mapping=node_parent_mapping,
            node_position_mapping=node_position_mapping,
            node_coordinate_mapping=node_coordinate_mapping,
            node_parent_group_mapping=node_parent_group_mapping,
            edge_label_mapping=edge_label_mapping,
            edge_property_mapping=edge_property_mapping,
            edge_color_mapping=edge_color_mapping,
            edge_styles_mapping=edge_styles_mapping,
            edge_thickness_factor_mapping=edge_thickness_factor_mapping,
            directed_mapping=directed_mapping
        )
        instance.import_graph(graph)
        return instance

    def show(self,
             directed=True,
             graph_layout=Layout.ORGANIC,
             sync_selection=False,
             sidebar={'enabled': False},
             neighborhood={'max_distance': 1, 'selected_nodes': []},
             overview=True,
             key=None):
        """Create a new instance of "StreamlitGraphWidget".

        Parameters
        ----------
        directed: bool
            A boolean whether the edges show a direction indicator. By default, `True`.
        graph_layout: Layout
            An optional argument specifying the starting layout
        sync_selection: bool
            Whether the component returns the lists of interactively selected nodes and edges. Enabling this may require caching the component to avoid excessive rerendering.
        sidebar: Dict
            The sidebar starting configuration
        neighborhood: Dict
            The neighborhood tab starting configuration
        overview: bool
            Whether the overview is expanded
        key: str or None
            An optional key that uniquely identifies this component. If this is
            None, and the component's arguments are changed, the component will
            be re-mounted in the Streamlit frontend and lose its current state.

        Returns
        -------
        selected_nodes, selected_edges
             Returns a reference to the interactively selected node- or edge-dicts iff `sync_selection` is set to `True`.

        """
        self._directed = directed
        self._mapper.apply_mappings()

        widget_overview = {'enabled': overview, 'overview_set': True}

        # only serializable dicts can be sent to the frontend
        sanitized_node_dicts = [
            make_json_safe(n.to_dict() if isinstance(n, Node) else n)
            for n in self.nodes
        ]
        sanitized_edge_dicts = [
            make_json_safe(e.to_dict() if isinstance(e, Edge) else e)
            for e in self.edges
        ]

        # call frontend
        selected_node_ids, selected_edge_ids = _component_func(
            nodes=sanitized_node_dicts,
            edges=sanitized_edge_dicts,
            directed=directed,
            graph_layout=graph_layout,
            _sidebar=sidebar,
            _neighborhood=neighborhood,
            _overview=widget_overview,
            sync_selection=sync_selection,
            key=key) or ([], [])

        # given the selected node/edge ids, return the actual node/edge objects
        selected_nodes = [n for n in self.nodes if n.get("id") in selected_node_ids]
        selected_edges = [e for e in self.edges if e.get("id") in selected_edge_ids]

        return selected_nodes, selected_edges
