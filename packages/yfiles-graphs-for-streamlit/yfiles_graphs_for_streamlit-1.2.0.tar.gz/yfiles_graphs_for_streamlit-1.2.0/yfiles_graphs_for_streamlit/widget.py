#!/usr/bin/env python
# coding: utf-8
"""The main GraphWidget class is defined in this module."""
import uuid
from typing import Dict as TDict, Optional, Any, Callable, Union, List, Tuple
import warnings

from .node import Node
from .edge import Edge
from .label_style import LabelStyle
from .node_style import NodeStyle
from .edge_style import EdgeStyle
from .layout.layout import Layout
from .graph_importer import import_
from .apply_mappings import MappingClass
from .layout import layout_
from .utils import COLOR_PALETTE, get_neo4j_item_text

class GraphWidget:
    """The main widget class."""

    def __init__(self) -> None:
        self._directed_mapping: Optional[Union[str, Callable[[dict], bool]]] = None
        self._edge_thickness_factor_mapping: Optional[Union[str, Callable[[dict], float]]] = None
        self._edge_styles_mapping: Optional[Union[str, Callable[[dict], EdgeStyle]]] = None
        self._edge_color_mapping: Optional[Union[str, Callable[[dict], str]]] = None
        self._edge_property_mapping: Optional[Union[str, Callable[[dict], dict]]] = None
        self._edge_label_mapping: Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]] = None
        self._node_parent_group_mapping: Optional[Union[str, Callable[[dict], Union[str, dict]]]] = None
        self._node_coordinate_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]] = None
        self._node_position_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]] = None
        self._node_parent_mapping: Optional[Union[str, Callable[[dict], Union[str, int, float]]]] = None
        self._node_type_mapping: Optional[Union[str, Callable[[dict], str]]] = None
        self._node_cell_mapping: Optional[Union[str, Callable[[dict], Tuple[int, int]]]] = None
        self._node_layout_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float, float, float]]]] = None
        self._node_size_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]] = None
        self._node_color_mapping: Optional[Union[str, Callable[[dict], str]]] = None
        self._node_property_mapping: Optional[Union[str, Callable[[dict], dict]]] = None
        self._node_scale_factor_mapping: Optional[Union[str, Callable[[dict], float]]] = None
        self._node_styles_mapping: Optional[Union[str, Callable[[dict], NodeStyle]]] = None
        self._node_label_mapping: Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]] = None
        self._heat_mapping: Optional[Union[str, Callable[[dict], float]]] = None

        self._selected_graph: Tuple[List[TDict], List[TDict]] = ([], [])
        self._graph_layout = layout_(Layout.ORGANIC, **{})
        self._overview: TDict[str, bool] = dict(enabled=True, overview_set=True)
        self._sidebar: Optional[TDict[str, Any]] = None
        self._neighborhood: Optional[TDict[str, Any]] = None

        self._edges: List[TDict[str, Any]] = []
        self._nodes: List[Union[Node, TDict[str, Any]]] = []
        self._error = None
        self._errorMessage = ''
        self._itemtype2colorIdx: TDict[str, int] = {}

        self._group_nodes: List[TDict[str, Any]] = []
        self._mapper = MappingClass(self)
        self._directed = False
        self._data_importer = 'unknown'


    # region Properties

    # region nodes
    def get_nodes(self):
        """Legacy getter for nodes property.

        Deprecated, use ``widget.nodes`` instead.
        """
        warnings.warn(
            "get_nodes() is deprecated; use `widget.nodes` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.nodes

    def set_nodes(self, nodes):
        """Legacy setter for nodes property.

        Deprecated, use ``widget.nodes = value`` instead.
        """
        warnings.warn(
            "set_nodes() is deprecated; use `widget.nodes = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.nodes = nodes

    @property
    def nodes(self) -> List[Union[Node, TDict[str, Any]]]:
        """Getter for the nodes property.

        Returns
        -------
        nodes: List[Dict]
            Each node has the keys id: int and properties: Dict.
            It might include keys that are not set directly,
            see (default) node mappings for details.
        """
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List[Union[Node, TDict[str, Any]]]) -> None:
        """Setter for the nodes property.

        Parameters
        ----------
        nodes: List[Dict]
            Each node should have the keys id: int and properties: Dict.
            Properties should be constructed recursively with basic python types,
            otherwise {de-}serializers will fail.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           w.set_nodes([
                {'id': 0, 'properties': {'label': 'Hello World'}},
                {'id': 1, 'properties': {'label': 'This is a second node.'}}
           ])

        Returns
        -------
        """
        if not isinstance(nodes, list):
            raise ValueError("Nodes must be a list of dictionaries.")
        for node in nodes:
            if not isinstance(node, (Node, dict)):
                raise ValueError("Each node object must be a 'Node'.")

            # Check required 'id' key
            if isinstance(node, dict) and 'id' not in node:
                raise ValueError("Each node must have an 'id' key.")
        self._nodes = nodes

    # endregion

    # region edges
    def get_edges(self):
        """Legacy getter for edges property.

        Deprecated, use ``widget.edges`` instead.
        """
        warnings.warn(
            "get_edges() is deprecated; use `widget.edges` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.edges

    def set_edges(self, edges):
        """Legacy setter for edges property.

        Deprecated, use ``widget.edges = value`` instead.
        """
        warnings.warn(
            "set_edges() is deprecated; use `widget.edges = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edges = edges

    @property
    def edges(self) -> List[Union[Edge, TDict[str, Any]]]:
        """Getter for the edges property.

        Returns
        -------
        edges: List[Dict]
            Each edge has the keys id: int, start: int, end: int and properties: Dict.
            It might include keys that are not set directly,
            see (default) edge mappings for details.
        """
        return self._edges

    @edges.setter
    def edges(self, edges: List[Union[Edge, TDict[str, Any]]]) -> None:
        """Setter for the edges property.

        Parameters
        ----------
        edges: List[Dict]
            Each edge should have the keys id: int, start: int, end: int and properties: Dict.
            Properties should be constructed recursively with basic python types,
            otherwise {de-}serializers will fail.

        Returns
        -------
        """
        if not isinstance(edges, list):
            raise ValueError("Edges must be a list of dictionaries.")
        for edge in edges:
            if not isinstance(edge, (Edge, dict)):
                raise ValueError("Each edge must be an Edge or a dictionary.")

            # Check required keys 'from' and 'to'
            if isinstance(edge, dict):
                if 'start' not in edge:
                    raise ValueError("Each edge must have a 'start' key.")
                if 'end' not in edge:
                    raise ValueError("Each edge must have a 'end' key.")

                # Add 'id' if missing
                if 'id' not in edge:
                    edge['id'] = str(uuid.uuid4())
        self._edges = edges
    # endregion

    # region directed
    def get_directed(self):
        """Legacy getter for directed property.

        Deprecated, use ``widget.directed`` instead.
        """
        warnings.warn(
            "get_directed() is deprecated; use `widget.directed` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.directed

    def set_directed(self, directed: bool) -> None:
        """Legacy setter for directed property.

        Deprecated, use ``widget.directed = value`` instead.
        """
        warnings.warn(
            "set_directed() is deprecated; use `widget.directed = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.directed = directed

    @property
    def directed(self) -> bool:
        """Getter for the directed property.

        Returns
        -------
        directed: bool
            Whether the graph is interpreted as directed.
        """
        return self._directed

    @directed.setter
    def directed(self, directed: bool) -> None:
        """Setter for the directed property.

        Parameters
        ----------
        directed: bool
            Whether the graph is interpreted as directed.
        """
        self._directed = directed
    # endregion

    # region neighborhood
    def get_neighborhood(self):
        """Legacy getter for neighborhood property.

        Deprecated, use ``widget.neighborhood`` instead.
        """
        warnings.warn(
            "get_neighborhood() is deprecated; use `widget.neighborhood` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._neighborhood

    def set_neighborhood(self, max_distance: int = 1, selected_nodes: Optional[list] = None):
        """Legacy setter for the neighborhood property.

        Deprecated, use ``widget.neighborhood = {...}`` or ``widget.neighborhood = 2`` instead.
        """
        warnings.warn(
            "set_neighborhood() is deprecated; use `widget.neighborhood = {...}` or an int instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if selected_nodes is None:
            selected_nodes = []
        self.neighborhood = {"max_distance": max_distance, "selected_nodes": selected_nodes}

    @property
    def neighborhood(self) -> Union[TDict[str, Any], None]:
        """Getter for the neighborhood property.

        Returns
        -------
        neighborhood: Dict
            Returned dict has keys max_distance: int and selected_nodes: list,
            a list of node ids.
        """
        return self._neighborhood

    @neighborhood.setter
    def neighborhood(self, value: Union[int, TDict[str, Any]]) -> None:
        """Specify the neighborhood view in the widget.

        The number of hops and focused nodes can be chosen.
        You may pass either an int (max_distance) or a dict with keys
        'max_distance' and 'selected_nodes'.
        """
        if isinstance(value, dict):
            max_distance = value.get('max_distance', 1)
            selected_nodes = value.get('selected_nodes', [])
        else:
            max_distance = int(value)
            selected_nodes = []
        self._neighborhood = dict(max_distance=max_distance, selected_nodes=selected_nodes)
    # endregion

    # region selection
    @property
    def selection(self) -> Tuple[List[TDict], List[TDict]]:
        """Getter for the exported selection.

        Returns
        -------
        nodes, edges: list[dict], list[dict]
            Each node has the keys ``id: int`` and ``properties: dict``.
            Each edge has the keys ``id: int``, ``start: int``, ``end: int`` and ``properties: dict``.
        """
        if not self._selected_graph:
            self._selected_graph = ([], [])
        return self._selected_graph

    def get_selection(self) -> Tuple[List[TDict], List[TDict]]:
        """Legacy getter for selection.

        Deprecated, use ``widget.selection`` instead.
        """
        warnings.warn(
            "get_selection() is deprecated; use `widget.selection` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.selection
    # endregion

    # region sidebar
    def get_sidebar(self):
        """Legacy getter for sidebar property.

        Deprecated, use ``widget.sidebar`` instead.
        """
        warnings.warn(
            "get_sidebar() is deprecated; use `widget.sidebar` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._sidebar

    def set_sidebar(self, enabled=True, start_with: str = ''):
        """Legacy setter for sidebar.

        Deprecated, use ``widget.sidebar = {...}`` or ``widget.sidebar = True/False`` instead.
        """
        warnings.warn(
            "set_sidebar() is deprecated; use `widget.sidebar = {...}` or a boolean instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.sidebar = {'enabled': enabled, 'start_with': start_with}

    @property
    def sidebar(self) -> Union[TDict[str, Any], None]:
        """Getter for the sidebar property.

        Returns
        -------
        sidebar: Dict
            Returned dict has keys enabled: bool and start_with: str,
            whereat the first one indicates open or closed sidebar and
            the second one indicates a start panel in the widget.
        """
        return self._sidebar

    @sidebar.setter
    def sidebar(self, value: Union[bool, TDict[str, Any]]) -> None:
        """Specify the appearance of the sidebar in the widget.

        Can be used to collapse sidebar or start with any panel.

        Parameters
        ----------
        value: bool | dict
            Either a boolean to open/collapse the sidebar, or a dict with keys
            'enabled' and 'start_with'.
        """
        if isinstance(value, dict):
            enabled = value.get('enabled', False)
            start_with = value.get('start_with', '')
        else:
            enabled = bool(value)
            start_with = ''
        self._sidebar = dict(enabled=enabled, start_with=start_with)
    # endregion

    # region overview
    @property
    def overview(self) -> bool:
        """Getter for the overview property.

        Returns
        -------
        overview: bool
            Indicates open or closed overview state.
        """
        return self._overview["enabled"]

    @overview.setter
    def overview(self, enabled: bool = True) -> None:
        """Specify the appearance of the overview component in the widget.

        Can be used to force the overview open in case of a small widget layout or
        force it collapsed in case of a large widget layout.

        Parameters
        ----------
        enabled: bool
            Whether to open or collapse the overview at widget startup.

        Returns
        -------
        None
        """
        self._overview = dict(enabled=enabled, overview_set=True)

    def get_overview(self) -> bool:
        """Legacy getter for overview.

        Deprecated, use ``widget.overview`` instead.
        """
        warnings.warn(
            "get_overview() is deprecated; use `widget.overview` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.overview

    def set_overview(self, enabled: bool = True) -> None:
        """Legacy setter for overview.

        Deprecated, use ``widget.overview = value`` instead.
        """
        warnings.warn(
            "set_overview() is deprecated; use `widget.overview = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.overview = enabled
    # endregion

    # region graph_layout
    @property
    def graph_layout(self) -> Layout:
        """Getter for the graph layout property.

        Returns
        -------
        graph_layout: Layout
        """
        return Layout(self._graph_layout.get("algorithm"))

    @graph_layout.setter
    def graph_layout(self, algorithm: Layout) -> None:
        """Choose graph layout.

        Currently, the algorithms use default settings from the yFiles library.

        Parameters
        ----------
        algorithm: str | dict
            Specify graph layout (or edge router) algorithm.
            Available algorithms are:
            ``["circular", "circular_straight_line", "hierarchic", "organic", "orthogonal", "radial",
            "tree", "orthogonal_edge_router", "organic_edge_router", "map", "no_layout"]``.
            May also be a dictionary, e.g. ``{"algorithm": "organic"}``.

        Notes
        -----
        This function acts as an alias for using ``GraphWidget.graph_layout`` property.
        For example, ``w.graph_layout = 'organic'`` has the same effect as ``w.set_graph_layout('organic')``.
        Setting ``w.graph_layout = {"algorithm": "organic"}`` works as well, which corresponds to using
        the value returned by the associated getter.

        In case you want to use edge routers, you should set a custom node position mapping as well.
        See yFiles documentation:
        https://docs.yworks.com/yfileshtml/#/dguide/layout-summary for more details about the algorithms.

        Returns
        -------
        None
        """

        layout_str = ''
        # keep dict handling for compatibility reasons
        if isinstance(algorithm, dict):
            _algorithm = algorithm
            layout_str = _algorithm.pop("algorithm", None)

        # unpack enum
        if isinstance(algorithm, Layout):
            layout_str = algorithm.value

        self._graph_layout = layout_(layout_str, **{})

    def get_graph_layout(self) -> Layout:
        """Legacy getter for graph_layout.

        Deprecated, use ``widget.graph_layout`` instead.
        """
        warnings.warn(
            "get_graph_layout() is deprecated; use `widget.graph_layout` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.graph_layout

    def set_graph_layout(self, algorithm: Layout) -> None:
        """Legacy setter for graph_layout.

        Deprecated, use ``widget.graph_layout = value`` instead.
        """
        warnings.warn(
            "set_graph_layout() is deprecated; use `widget.graph_layout = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.graph_layout = algorithm
    # endregion

    # endregion Properties

    # region Data Mappings

    # region heat_mapping
    @property
    def heat_mapping(self) -> Optional[Union[str, Callable[[dict], float]]]:
        """Getter for the heat mapping property.

        Returns
        -------
        heat_mapping: callable | str
            A function that produces heat values or the name of the property to use for the heat binding.

        """
        return self._heat_mapping

    @heat_mapping.setter
    def heat_mapping(self, heat_mapping: Optional[Union[str, Callable[[dict], float]]]) -> None:
        """Setter for the heat mapping property.

        Parameters
        ----------
        heat_mapping: callable | str
            A function that produces heat values or the name of the property to use for the heat binding.
            The function should have the same signature as `default_heat_mapping`
            e.g., take in a dictionary and return a number.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_heat_mapping(node: dict):
           ...
           w.set_heat_mapping(custom_heat_mapping)

        Returns
        -------

        """
        self._heat_mapping = heat_mapping

    def get_heat_mapping(self) -> Optional[Union[str, Callable[[dict], float]]]:
        """Legacy getter for heat_mapping.

        Deprecated, use ``widget.heat_mapping = value`` instead.
        """
        warnings.warn(
            "set_heat_mapping() is deprecated; use `widget.heat_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.heat_mapping

    def set_heat_mapping(self, heat_mapping: Optional[Union[str, Callable[[dict], float]]]) -> None:
        """Legacy setter for heat_mapping.

        Deprecated, use ``widget.heat_mapping = value`` instead.
        """
        warnings.warn(
            "set_heat_mapping() is deprecated; use `widget.heat_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.heat_mapping = heat_mapping

    def del_heat_mapping(self) -> None:
        """Legacy deleter for heat_mapping.

        Deprecated, use ``widget.heat_mapping = None`` instead.
        """
        warnings.warn(
            "del_heat_mapping() is deprecated; use `widget.heat_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.heat_mapping = None
    # endregion

    # region Node Mappings

    # region node_label_mapping
    @property
    def node_label_mapping(self) -> Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]]:
        """Getter for the node label mapping property.

        Returns
        -------
        node_label_mapping: callable | str
            A function that produces node labels or the name of the property to use for the label binding.
        """
        return self._node_label_mapping

    @node_label_mapping.setter
    def node_label_mapping(self, node_label_mapping: Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]]) -> None:
        """Setter for the node label mapping property.

        Parameters
        ----------
        node_label_mapping: callable | str
            A function that produces node labels or the name of the property to use for the label binding.
            The function should have the same signature as `default_node_label_mapping`
            e.g., take in a node dictionary and return a string.

        Example
        -------

        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           w.node_label_mapping = 'id'

        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_label_mapping(node: dict):
           ...
           w.set_node_label_mapping(custom_node_label_mapping)

        Returns
        -------

        """
        self._node_label_mapping = node_label_mapping

    def get_node_label_mapping(self) -> Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]]:
        """Legacy getter for node_label_mapping.

        Deprecated, use ``widget.node_label_mapping`` instead.
        """
        warnings.warn(
            "get_node_label_mapping() is deprecated; use `widget.node_label_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_label_mapping

    def set_node_label_mapping(self, node_label_mapping: Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]]) -> None:
        """Legacy setter for node_label_mapping.

        Deprecated, use ``widget.node_label_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_label_mapping() is deprecated; use `widget.node_label_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_label_mapping = node_label_mapping

    def del_node_label_mapping(self) -> None:
        """Legacy deleter for node_label_mapping.

        Deprecated, use ``widget.node_label_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_label_mapping() is deprecated; use `widget.node_label_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_label_mapping = None
    # endregion

    # region node_property_mapping
    @property
    def node_property_mapping(self) -> Optional[Union[str, Callable[[dict], dict]]]:
        """Getter for the node property mapping property.

        Returns
        -------
        node_property_mapping: callable | str | None
            A function that produces node properties or the name of the property to use for the property binding,
            or ``None`` if no mapping is currently set.
        """
        return self._node_property_mapping


    @node_property_mapping.setter
    def node_property_mapping(self, node_property_mapping: Optional[Union[str, Callable[[dict], dict]]]) -> None:
        """Setter for the node property mapping property.

        Parameters
        ----------
        node_property_mapping: callable | str | None
            A function that produces node properties or the name of the property to use for the property binding.
            The function should have the same signature as `default_node_property_mapping`,
            e.g., take in a node dictionary and return a dictionary.
            If ``None`` is passed, this unsets the mapping.

        Notes
        -----
        Properties are changed in place by this mapping.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_node_property_mapping(node: dict):
               ...
           w.node_property_mapping = custom_node_property_mapping

        Returns
        -------
        None
        """
        self._node_property_mapping = node_property_mapping


    def get_node_property_mapping(self) -> Optional[Union[str, Callable[[dict], dict]]]:
        """Legacy getter for node_property_mapping.

        Deprecated, use ``widget.node_property_mapping`` instead.
        """
        warnings.warn(
            "get_node_property_mapping() is deprecated; use `widget.node_property_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_property_mapping


    def set_node_property_mapping(self, node_property_mapping: Optional[Union[str, Callable[[dict], dict]]]) -> None:
        """Legacy setter for node_property_mapping.

        Deprecated, use ``widget.node_property_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_property_mapping() is deprecated; use `widget.node_property_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_property_mapping = node_property_mapping


    def del_node_property_mapping(self) -> None:
        """Legacy deleter for node_property_mapping.

        Deprecated, use ``widget.node_property_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_property_mapping() is deprecated; use `widget.node_property_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_property_mapping = None
    # endregion

    # region node_color_mapping
    @property
    def node_color_mapping(self) -> Optional[Union[str, Callable[[dict], str]]]:
        """Getter for the node color mapping property.

        Returns
        -------
        node_color_mapping: callable | str | None
            A function that produces node colors or the name of the property to use for the color binding,
            or ``None`` if no mapping is currently set.
        """
        return self._node_color_mapping


    @node_color_mapping.setter
    def node_color_mapping(self, node_color_mapping: Optional[Union[str, Callable[[dict], str]]]) -> None:
        """Setter for the node color mapping property.

        Parameters
        ----------
        node_color_mapping: callable | str | None
            A function that produces node colors or the name of the property to use for the color binding.
            The function should have the same signature as `default_node_color_mapping`,
            e.g., take in a node dictionary and return a string.
            If ``None`` is passed, this unsets the mapping.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_node_color_mapping(node: dict):
               ...
           w.node_color_mapping = custom_node_color_mapping

        Returns
        -------
        None
        """
        self._node_color_mapping = node_color_mapping

    def get_node_color_mapping(self) -> Optional[Union[str, Callable[[dict], str]]]:
        """Legacy getter for node_color_mapping.

        Deprecated, use ``widget.node_color_mapping`` instead.
        """
        warnings.warn(
            "get_node_color_mapping() is deprecated; use `widget.node_color_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_color_mapping


    def set_node_color_mapping(self, node_color_mapping: Optional[Union[str, Callable[[dict], str]]]) -> None:
        """Legacy setter for node_color_mapping.

        Deprecated, use ``widget.node_color_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_color_mapping() is deprecated; use `widget.node_color_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_color_mapping = node_color_mapping


    def del_node_color_mapping(self) -> None:
        """Legacy deleter for node_color_mapping.

        Deprecated, use ``widget.node_color_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_color_mapping() is deprecated; use `widget.node_color_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_color_mapping = None
    # endregion

    # region node_styles_mapping
    @property
    def node_styles_mapping(self) -> Optional[Union[str, Callable[[dict], NodeStyle]]]:
        """Getter for the node styles mapping property.

        Returns
        -------
        node_styles_mapping: callable | str
            A function that produces node styles or the name of the property to use for the style object binding.

        """
        return self._node_styles_mapping

    @node_styles_mapping.setter
    def node_styles_mapping(self, node_styles_mapping: Optional[Union[str, Callable[[dict], NodeStyle]]]) -> None:
        """Setter for the node styles mapping property.

        Parameters
        ----------
        node_styles_mapping: callable | str
            A function that produces node styles or the name of the property to use for the style object binding.
            The function should have the same signature as `default_node_styles_mapping`
            e.g., take in a node dictionary and return a Dict.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_styles_mapping(node: dict):
           ...
           w.set_node_styles_mapping(custom_node_styles_mapping)

        Returns
        -------

        """
        self._node_styles_mapping = node_styles_mapping

    def get_node_styles_mapping(self) -> Optional[Union[str, Callable[[dict], NodeStyle]]]:
        """Legacy getter for the node styles mapping property.

        Deprecated, use ``widget.node_styles_mapping`` instead.
        """
        warnings.warn(
            "get_node_styles_mapping() is deprecated; use `widget.node_styles_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_styles_mapping

    def set_node_styles_mapping(self, node_styles_mapping: Optional[Union[str, Callable[[dict], NodeStyle]]]) -> None:
        """Legacy setter for the node styles mapping property.

        Deprecated, use ``widget.node_styles_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_styles_mapping() is deprecated; use `widget.node_styles_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_styles_mapping = node_styles_mapping

    def del_node_styles_mapping(self) -> None:
        """Deleter for the node styles mapping property.

        Deprecated, use ``widget.node_styles_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_styles_mapping() is deprecated; use `widget.node_styles_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_styles_mapping = None
    # endregion

    # region node_scale_factor_mapping
    @property
    def node_scale_factor_mapping(self) -> Optional[Union[str, Callable[[dict], float]]]:
        """Getter for the node scale factor mapping property.

        Returns
        -------
        node_scale_factor_mapping: callable | str
            A function that produces node scale factor or the name of the property to use for the scale binding.

        """
        return self._node_scale_factor_mapping

    @node_scale_factor_mapping.setter
    def node_scale_factor_mapping(self, node_scale_factor_mapping: Optional[Union[str, Callable[[dict], float]]]) -> None:
        """Setter for the node scale factor mapping property.

        Parameters
        ----------
        node_scale_factor_mapping: callable | str
            A function that produces node scale factors or the name of the property to use for the scale binding.
            The function should have the same signature as `default_node_scale_factor_mapping`
            e.g., take in a node dictionary and return a positive float.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_scale_factor_mapping(node: dict):
           ...
           w.set_node_scale_factor_mapping(custom_node_scale_factor_mapping)

        Returns
        -------

        """
        self._node_scale_factor_mapping = node_scale_factor_mapping

    def get_node_scale_factor_mapping(self) -> Optional[Union[str, Callable[[dict], float]]]:
        """Legacy getter for node_scale_factor_mapping.

        Deprecated, use ``widget.node_scale_factor_mapping`` instead.
        """
        warnings.warn(
            "get_node_scale_factor_mapping() is deprecated; use `widget.node_scale_factor_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_scale_factor_mapping


    def set_node_scale_factor_mapping(self, node_scale_factor_mapping: Optional[Union[str, Callable[[dict], float]]]) -> None:
        """Legacy setter for node_scale_factor_mapping.

        Deprecated, use ``widget.node_scale_factor_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_scale_factor_mapping() is deprecated; use `widget.node_scale_factor_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_scale_factor_mapping = node_scale_factor_mapping

    def del_node_scale_factor_mapping(self) -> None:
        """Legacy deleter for node_scale_factor_mapping.

        Deprecated, use ``widget.node_scale_factor_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_scale_factor_mapping() is deprecated; use `widget.node_scale_factor_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_scale_factor_mapping = None
    # endregion

    # region node_size_mapping
    @property
    def node_size_mapping(self) -> Optional[Union[str, Callable[[dict], Tuple[float, float]]]]:
        """Getter for the node size mapping property.

        Returns
        -------
        node_size_mapping: callable | str | None
            A function that produces node sizes or the name of the property to use for the size binding,
            or ``None`` if no mapping is currently set.
        """
        return self._node_size_mapping


    @node_size_mapping.setter
    def node_size_mapping(self, node_size_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]]) -> None:
        """Setter for the node size mapping property.

        Parameters
        ----------
        node_size_mapping: callable | str | None
            A function that produces node sizes or the name of the property to use for the size binding.
            The function should have the same signature as `default_node_size_mapping`,
            e.g., take in an index and a node dictionary and return a positive number.
            If ``None`` is passed, this unsets the mapping.

        Returns
        -------
        None
        """
        self._node_size_mapping = node_size_mapping


    def get_node_size_mapping(self) -> Optional[Union[str, Callable[[dict], Tuple[float, float]]]]:
        """Legacy getter for node_size_mapping.

        Deprecated, use ``widget.node_size_mapping`` instead.
        """
        warnings.warn(
            "get_node_size_mapping() is deprecated; use `widget.node_size_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_size_mapping


    def set_node_size_mapping(self, node_size_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]]) -> None:
        """Legacy setter for node_size_mapping.

        Deprecated, use ``widget.node_size_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_size_mapping() is deprecated; use `widget.node_size_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_size_mapping = node_size_mapping


    def del_node_size_mapping(self) -> None:
        """Legacy deleter for node_size_mapping.

        Deprecated, use ``widget.node_size_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_size_mapping() is deprecated; use `widget.node_size_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_size_mapping = None
    # endregion

    # region node_layout_mapping
    @property
    def node_layout_mapping(self) -> Optional[Union[str, Callable[[dict], Tuple[float, float, float, float]]]]:
        """Getter for the node layout mapping property.

        Returns
        -------
        node_layout_mapping: callable | str | None
            A function that produces node layouts or the name of the property to use for the layout binding,
            or ``None`` if no mapping is currently set.
        """
        return self._node_layout_mapping


    @node_layout_mapping.setter
    def node_layout_mapping(
            self, node_layout_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float, float, float]]]]
    ) -> None:
        """Setter for the node layout mapping property.

        Parameters
        ----------
        node_layout_mapping: callable | str | None
            A function that produces node layouts or the name of the property to use for the layout binding.
            The function should have the same signature as `default_node_layout_mapping`,
            e.g., take in an index and a node dictionary and return a positive float 4‑tuple.
            If ``None`` is passed, this unsets the mapping.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_node_layout_mapping(node: dict):
               ...
           w.node_layout_mapping = custom_node_layout_mapping

        Returns
        -------
        None
        """
        self._node_layout_mapping = node_layout_mapping

    def get_node_layout_mapping(self) -> Optional[Union[str, Callable[[dict], Tuple[float, float, float, float]]]]:
        """Legacy getter for node_layout_mapping.

        Deprecated, use ``widget.node_layout_mapping`` instead.
        """
        warnings.warn(
            "get_node_layout_mapping() is deprecated; use `widget.node_layout_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_layout_mapping


    def set_node_layout_mapping(
            self, node_layout_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float, float, float]]]]
    ) -> None:
        """Legacy setter for node_layout_mapping.

        Deprecated, use ``widget.node_layout_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_layout_mapping() is deprecated; use `widget.node_layout_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_layout_mapping = node_layout_mapping

    def del_node_layout_mapping(self) -> None:
        """Legacy deleter for node_layout_mapping.

        Deprecated, use ``widget.node_layout_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_layout_mapping() is deprecated; use `widget.node_layout_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_layout_mapping = None
    # endregion

    # region node_cell_mapping
    @property
    def node_cell_mapping(self) -> Optional[Union[str, Callable[[dict], Tuple[int, int]]]]:
        """Getter for the node cell index mapping property.

        Returns
        -------
        node_cell_mapping: callable | str | None
            A function that produces node cell indices or the name of the property to use for the cell index binding,
            or ``None`` if no mapping is currently set.
        """
        return self._node_cell_mapping

    @node_cell_mapping.setter
    def node_cell_mapping(self, node_cell_mapping: Optional[Union[str, Callable[[dict], Tuple[int, int]]]]) -> None:
        """Setter for the node cell index mapping property.

        Parameters
        ----------
        node_cell_mapping: callable | str | None
            A function that produces node cell indices or the name of the property to use for the cell index binding.
            The function consumes a node object and should return a tuple ``(row, column)`` for the cell index.
            If ``None`` is passed, this unsets the mapping.

        Returns
        -------
        None
        """
        self._node_cell_mapping = node_cell_mapping

    def get_node_cell_mapping(self) -> Optional[Union[str, Callable[[dict], Tuple[int, int]]]]:
        """Legacy getter for node_cell_mapping.

        Deprecated, use ``widget.node_cell_mapping`` instead.
        """
        warnings.warn(
            "get_node_cell_mapping() is deprecated; use `widget.node_cell_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_cell_mapping

    def set_node_cell_mapping(self, node_cell_mapping: Optional[Union[str, Callable[[dict], Tuple[int, int]]]]) -> None:
        """Legacy setter for node_cell_mapping.

        Deprecated, use ``widget.node_cell_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_cell_mapping() is deprecated; use `widget.node_cell_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_cell_mapping = node_cell_mapping

    def del_node_cell_mapping(self) -> None:
        """Legacy deleter for node_cell_mapping.

        Deprecated, use ``widget.node_cell_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_cell_mapping() is deprecated; use `widget.node_cell_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_cell_mapping = None
    # endregion

    # region node_type_mapping
    @property
    def node_type_mapping(self) -> Optional[Union[str, Callable[[dict], str]]]:
        """Getter for the node type mapping property.

        Returns
        -------
        node_type_mapping: callable | str | None
            A function that produces node types or the name of the property to use for the type binding,
            or ``None`` if no mapping is currently set.
        """
        return self._node_type_mapping


    @node_type_mapping.setter
    def node_type_mapping(self, node_type_mapping: Optional[Union[str, Callable[[dict], str]]]) -> None:
        """Setter for the node type mapping property.

        Parameters
        ----------
        node_type_mapping: callable | str | None
            A function that produces node types or the name of the property to use for the type binding.
            The function should have the same signature as `default_node_type_mapping`,
            e.g., take in a node dictionary and return a bool, int, float, or str value.
            If ``None`` is passed, this unsets the mapping.

        Notes
        -----
        Node types give more information for some layout algorithms.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_node_type_mapping(node: dict):
               ...
           w.node_type_mapping = custom_node_type_mapping

        References
        ----------
        Layout with Custom Node Types
        <https://docs.yworks.com/yfileshtml/#/dguide/layout-summary#node_types>

        Returns
        -------
        None
        """
        self._node_type_mapping = node_type_mapping

    def get_node_type_mapping(self) -> Optional[Union[str, Callable[[dict], str]]]:
        """Legacy getter for node_type_mapping.

        Deprecated, use ``widget.node_type_mapping`` instead.
        """
        warnings.warn(
            "get_node_type_mapping() is deprecated; use `widget.node_type_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_type_mapping

    def set_node_type_mapping(self, node_type_mapping: Optional[Union[str, Callable[[dict], str]]]) -> None:
        """Legacy setter for node_type_mapping.

        Deprecated, use ``widget.node_type_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_type_mapping() is deprecated; use `widget.node_type_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_type_mapping = node_type_mapping

    def del_node_type_mapping(self) -> None:
        """Legacy deleter for node_type_mapping.

        Deprecated, use ``widget.node_type_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_type_mapping() is deprecated; use `widget.node_type_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_type_mapping = None
    # endregion

    # region node_parent_mapping
    @property
    def node_parent_mapping(self) -> Optional[Union[str, Callable[[dict], Union[str, int, float]]]]:
        """Getter for the node parent mapping property to create a nested graph hierarchy.

        Returns
        -------
        node_parent_mapping: callable | str | None
            A function that produces node parent IDs or the name of the property to use for the parent binding,
            or ``None`` if no mapping is currently set.
        """
        return self._node_parent_mapping

    @node_parent_mapping.setter
    def node_parent_mapping(self, node_parent_mapping: Optional[Union[str, Callable[[dict], Union[str, int, float]]]]) -> None:
        """Setter for the node parent mapping property.

        Parameters
        ----------
        node_parent_mapping: callable | str | None
            A function that produces node parent IDs or the name of the property to use for the parent binding.
            The function should have the same signature as `default_node_parent_mapping`,
            e.g., take in a node dictionary and return a ``str`` or ``None`` value.
            If ``None`` is passed, this unsets the mapping.
            It is expected that the returned value corresponds to the ID of another node (see `nodes`). This parent node
            is then created as a group node that groups the corresponding child nodes.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_node_parent_mapping(node: dict):
               ...
           w.node_parent_mapping = custom_node_parent_mapping

        Returns
        -------
        None
        """
        self._node_parent_mapping = node_parent_mapping

    def get_node_parent_mapping(self) -> Optional[Union[str, Callable[[dict], Union[str, int, float]]]]:
        """Legacy getter for node_parent_mapping.

        Deprecated, use ``widget.node_parent_mapping`` instead.
        """
        warnings.warn(
            "get_node_parent_mapping() is deprecated; use `widget.node_parent_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_parent_mapping

    def set_node_parent_mapping(self, node_parent_mapping: Optional[Union[str, Callable[[dict], Union[str, int, float]]]]) -> None:
        """Legacy setter for node_parent_mapping.

        Deprecated, use ``widget.node_parent_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_parent_mapping() is deprecated; use `widget.node_parent_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_parent_mapping = node_parent_mapping

    def del_node_parent_mapping(self) -> None:
        """Legacy deleter for node_parent_mapping.

        Deprecated, use ``widget.node_parent_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_parent_mapping() is deprecated; use `widget.node_parent_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_parent_mapping = None
    # endregion

    # region node_position_mapping
    @property
    def node_position_mapping(self) -> Optional[Union[str, Callable[[dict], Tuple[float, float]]]]:
        """Getter for the node position mapping property.

        Returns
        -------
        node_position_mapping: callable | str | None
            A function that produces node positions or the name of the property to use for position binding,
            or ``None`` if no mapping is currently set.
        """
        return self._node_position_mapping

    @node_position_mapping.setter
    def node_position_mapping(self, node_position_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]]) -> None:
        """Setter for the node position mapping property.

        Parameters
        ----------
        node_position_mapping: callable | str | None
            A function that produces node positions or the name of the property to use for the position binding.
            The function should have the same signature as `default_node_position_mapping`,
            e.g., take in a node dictionary and return a float 2‑tuple.
            If ``None`` is passed, this unsets the mapping.

        Notes
        -----
        Only edge router algorithms consider node positions,
        all other algorithms calculate node positions themselves.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_node_position_mapping(node: dict):
               ...
           w.node_position_mapping = custom_node_position_mapping

        Returns
        -------
        None
        """
        self._node_position_mapping = node_position_mapping

    def get_node_position_mapping(self) -> Optional[Union[str, Callable[[dict], Tuple[float, float]]]]:
        """Legacy getter for node_position_mapping.

        Deprecated, use ``widget.node_position_mapping`` instead.
        """
        warnings.warn(
            "get_node_position_mapping() is deprecated; use `widget.node_position_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_position_mapping

    def set_node_position_mapping(self, node_position_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]]) -> None:
        """Legacy setter for node_position_mapping.

        Deprecated, use ``widget.node_position_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_position_mapping() is deprecated; use `widget.node_position_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_position_mapping = node_position_mapping

    def del_node_position_mapping(self) -> None:
        """Legacy deleter for node_position_mapping.

        Deprecated, use ``widget.node_position_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_position_mapping() is deprecated; use `widget.node_position_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_position_mapping = None
    # endregion

    # region node_coordinate_mapping
    @property
    def node_coordinate_mapping(self) -> Optional[Union[str, Callable[[dict], Tuple[float, float]]]]:
        """Getter for the node coordinate mapping property.

        Returns
        -------
        node_coordinate_mapping: callable | str | None
            A function that produces node coordinates or the name of the property to use for coordinate binding,
            or ``None`` if no mapping is currently set.
        """
        return self._node_coordinate_mapping

    @node_coordinate_mapping.setter
    def node_coordinate_mapping(self, node_coordinate_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]]) -> None:
        """Setter for the node coordinate mapping property.

        Parameters
        ----------
        node_coordinate_mapping: callable | str | None
            A function that produces node coordinates or the name of the property to use for the coordinate binding.
            The function should have the same signature as `default_node_coordinate_mapping`,
            e.g., take in a node dictionary and return a float 2‑tuple.
            If ``None`` is passed, this unsets the mapping.

        Notes
        -----
        Only edge router algorithms consider node coordinates,
        all other algorithms calculate node coordinates themselves.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_node_coordinate_mapping(node: dict):
               ...
           w.node_coordinate_mapping = custom_node_coordinate_mapping

        Returns
        -------
        None
        """
        self._node_coordinate_mapping = node_coordinate_mapping

    def get_node_coordinate_mapping(self) -> Optional[Union[str, Callable[[dict], Tuple[float, float]]]]:
        """Legacy getter for node_coordinate_mapping.

        Deprecated, use ``widget.node_coordinate_mapping`` instead.
        """
        warnings.warn(
            "get_node_coordinate_mapping() is deprecated; use `widget.node_coordinate_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_coordinate_mapping

    def set_node_coordinate_mapping(self, node_coordinate_mapping: Optional[Union[str, Callable[[dict], Tuple[float, float]]]]) -> None:
        """Legacy setter for node_coordinate_mapping.

        Deprecated, use ``widget.node_coordinate_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_coordinate_mapping() is deprecated; use `widget.node_coordinate_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_coordinate_mapping = node_coordinate_mapping

    def del_node_coordinate_mapping(self) -> None:
        """Legacy deleter for node_coordinate_mapping.

        Deprecated, use ``widget.node_coordinate_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_coordinate_mapping() is deprecated; use `widget.node_coordinate_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_coordinate_mapping = None
    # endregion

    # region node_parent_group_mapping
    @property
    def node_parent_group_mapping(self) -> Optional[Union[str, Callable[[dict], Union[str, dict]]]]:
        """Getter for the node parent node mapping property to create a nested graph hierarchy.

        Returns
        -------
        node_parent_group_mapping: callable | str | None
            A function that produces node parent IDs or the name of the property to use for the parent binding,
            or ``None`` if no mapping is currently set.
        """
        return self._node_parent_group_mapping

    @node_parent_group_mapping.setter
    def node_parent_group_mapping(
            self,
            node_parent_group_mapping: Optional[Union[str, Callable[[dict], Union[str, dict]]]],
    ) -> None:
        """Setter for the parent group mapping property.

        Parameters
        ----------
        node_parent_group_mapping: callable | str | None
            In contrast to `node_parent_mapping`, this mapping creates new node objects instead of resolving
            against the existing node data.
            For ``str`` values, the mapping first tries to resolve the given string against the node's properties,
            which must resolve to a ``str`` that is used as the node's parent group id (and text label).
            For ``callable`` values, the mapping is called with the node for which the parent should be created as
            argument (same signature as `default_node_parent_group_mapping`). The callable should either
            return a ``str`` (resolved as described above), or a ``dict`` with a ``label`` property and any additional
            optional properties used as group label (and id) and additional data for that group. Returning ``None``
            results in no parent group being created for that node.
            If ``None`` is passed, this unsets the mapping.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_node_parent_group_mapping(node: dict):
               ...
           w.node_parent_group_mapping = custom_node_parent_group_mapping

        Returns
        -------
        None
        """
        self._node_parent_group_mapping = node_parent_group_mapping

    def get_node_parent_group_mapping(self) -> Optional[Union[str, Callable[[dict], Union[str, dict]]]]:
        """Legacy getter for node_parent_group_mapping.

        Deprecated, use ``widget.node_parent_group_mapping`` instead.
        """
        warnings.warn(
            "get_node_parent_group_mapping() is deprecated; use `widget.node_parent_group_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_parent_group_mapping

    def set_node_parent_group_mapping(
            self, node_parent_group_mapping: Optional[Union[str, Callable[[dict], Union[str, dict]]]]
    ) -> None:
        """Legacy setter for node_parent_group_mapping.

        Deprecated, use ``widget.node_parent_group_mapping = value`` instead.
        """
        warnings.warn(
            "set_node_parent_group_mapping() is deprecated; use `widget.node_parent_group_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_parent_group_mapping = node_parent_group_mapping

    def del_node_parent_group_mapping(self) -> None:
        """Legacy deleter for node_parent_group_mapping.

        Deprecated, use ``widget.node_parent_group_mapping = None`` instead.
        """
        warnings.warn(
            "del_node_parent_group_mapping() is deprecated; use `widget.node_parent_group_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_parent_group_mapping = None
    # endregion

    # endregion Node Mappings

    # region Edge Mappings

    # region edge_label_mapping
    @property
    def edge_label_mapping(self) -> Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]]:
        """Getter for the edge label mapping property.

        Returns
        -------
        edge_label_mapping: callable | str | None
            A function that produces edge labels or the name of the property to use for the label binding,
            or ``None`` if no mapping is currently set.
        """
        return self._edge_label_mapping

    @edge_label_mapping.setter
    def edge_label_mapping(self, edge_label_mapping: Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]]) -> None:
        """Setter for the edge label mapping property.

        Parameters
        ----------
        edge_label_mapping: callable | str | None
            A function that produces edge labels or the name of the property to use for the label binding.
            The function should have the same signature as `default_edge_label_mapping`,
            e.g., take in an edge dictionary and return a string.
            If ``None`` is passed, this unsets the mapping.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           w.edge_label_mapping = 'id'

        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_edge_label_mapping(edge: dict):
               ...
           w.edge_label_mapping = custom_edge_label_mapping

        Returns
        -------
        None
        """
        self._edge_label_mapping = edge_label_mapping

    def get_edge_label_mapping(self) -> Optional[Union[str, Callable[[dict], Union[str, LabelStyle]]]]:
        """Legacy getter for edge_label_mapping.

        Deprecated, use ``widget.edge_label_mapping`` instead.
        """
        warnings.warn(
            "get_edge_label_mapping() is deprecated; use `widget.edge_label_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.edge_label_mapping

    def set_edge_label_mapping(self, edge_label_mapping: Optional[Union[str, Callable[[dict], str]]]) -> None:
        """Legacy setter for edge_label_mapping.

        Deprecated, use ``widget.edge_label_mapping = value`` instead.
        """
        warnings.warn(
            "set_edge_label_mapping() is deprecated; use `widget.edge_label_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edge_label_mapping = edge_label_mapping

    def del_edge_label_mapping(self) -> None:
        """Legacy deleter for edge_label_mapping.

        Deprecated, use ``widget.edge_label_mapping = None`` instead.
        """
        warnings.warn(
            "del_edge_label_mapping() is deprecated; use `widget.edge_label_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edge_label_mapping = None
    # endregion

    # region edge_property_mapping
    @property
    def edge_property_mapping(self) -> Optional[Union[str, Callable[[dict], dict]]]:
        """Getter for the edge property mapping property.

        Returns
        -------
        edge_property_mapping: callable | str | None
            A function that produces edge properties or the name of the property to use for the property binding,
            or ``None`` if no mapping is currently set.
        """
        return self._edge_property_mapping

    @edge_property_mapping.setter
    def edge_property_mapping(self, edge_property_mapping: Optional[Union[str, Callable[[dict], dict]]]) -> None:
        """Setter for the edge property mapping property.

        Parameters
        ----------
        edge_property_mapping: callable | str | None
            A function that produces edge properties or the name of the property to use for the property binding.
            The function should have the same signature as `default_edge_property_mapping`,
            e.g., take in an edge dictionary and return a dictionary.
            If ``None`` is passed, this unsets the mapping.

        Notes
        -----
        Properties are changed in place by this mapping.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_edge_property_mapping(edge: dict):
               ...
           w.edge_property_mapping = custom_edge_property_mapping

        Returns
        -------
        None
        """
        self._edge_property_mapping = edge_property_mapping

    def get_edge_property_mapping(self) -> Optional[Union[str, Callable[[dict], dict]]]:
        """Legacy getter for edge_property_mapping.

        Deprecated, use ``widget.edge_property_mapping`` instead.
        """
        warnings.warn(
            "get_edge_property_mapping() is deprecated; use `widget.edge_property_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.edge_property_mapping

    def set_edge_property_mapping(self, edge_property_mapping: Optional[Union[str, Callable[[dict], dict]]]) -> None:
        """Legacy setter for edge_property_mapping.

        Deprecated, use ``widget.edge_property_mapping = value`` instead.
        """
        warnings.warn(
            "set_edge_property_mapping() is deprecated; use `widget.edge_property_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edge_property_mapping = edge_property_mapping

    def del_edge_property_mapping(self) -> None:
        """Legacy deleter for edge_property_mapping.

        Deprecated, use ``widget.edge_property_mapping = None`` instead.
        """
        warnings.warn(
            "del_edge_property_mapping() is deprecated; use `widget.edge_property_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edge_property_mapping = None
    # endregion

    # region edge_color_mapping
    @property
    def edge_color_mapping(self) -> Optional[Union[str, Callable[[dict], str]]]:
        """Getter for the edge color mapping property.

        Returns
        -------
        edge_color_mapping: callable | str | None
            A function that produces edge colors or the name of the property to use for the color binding,
            or ``None`` if no mapping is currently set.
        """
        return self._edge_color_mapping

    @edge_color_mapping.setter
    def edge_color_mapping(self, edge_color_mapping: Optional[Union[str, Callable[[dict], str]]]) -> None:
        """Setter for the edge color mapping property.

        Parameters
        ----------
        edge_color_mapping: callable | str | None
            A function that produces edge colors or the name of the property to use for the color binding.
            The function should have the same signature as `default_edge_color_mapping`,
            e.g., take in an edge dictionary and return a string.
            If ``None`` is passed, this unsets the mapping.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_edge_color_mapping(edge: dict):
               ...
           w.edge_color_mapping = custom_edge_color_mapping

        Returns
        -------
        None
        """
        self._edge_color_mapping = edge_color_mapping

    def get_edge_color_mapping(self) -> Optional[Union[str, Callable[[dict], str]]]:
        """Legacy getter for edge_color_mapping.

        Deprecated, use ``widget.edge_color_mapping`` instead.
        """
        warnings.warn(
            "get_edge_color_mapping() is deprecated; use `widget.edge_color_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.edge_color_mapping

    def set_edge_color_mapping(self, edge_color_mapping: Optional[Union[str, Callable[[dict], str]]]) -> None:
        """Legacy setter for edge_color_mapping.

        Deprecated, use ``widget.edge_color_mapping = value`` instead.
        """
        warnings.warn(
            "set_edge_color_mapping() is deprecated; use `widget.edge_color_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edge_color_mapping = edge_color_mapping

    def del_edge_color_mapping(self) -> None:
        """Legacy deleter for edge_color_mapping.

        Deprecated, use ``widget.edge_color_mapping = None`` instead.
        """
        warnings.warn(
            "del_edge_color_mapping() is deprecated; use `widget.edge_color_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edge_color_mapping = None
    # endregion

    # region edge_styles_mapping
    @property
    def edge_styles_mapping(self) -> Optional[Union[str, Callable[[dict], EdgeStyle]]]:
        """Getter for the edge styles mapping property.

        Returns
        -------
        edge_styles_mapping: callable | str | None
            A function that produces edge styles or the name of the property to use for the style object binding,
            or ``None`` if no mapping is currently set.
        """
        return self._edge_styles_mapping

    @edge_styles_mapping.setter
    def edge_styles_mapping(self, edge_styles_mapping: Optional[Union[str, Callable[[dict], EdgeStyle]]]) -> None:
        """Setter for the edge styles mapping property.

        Parameters
        ----------
        edge_styles_mapping: callable | dict | None
            A function that produces edge style properties or the name of the property to use for the style object binding.
            The function should have the same signature as `default_edge_styles_mapping`,
            e.g., take in an edge dictionary and return a ``dict``.
            If ``None`` is passed, this unsets the mapping.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_edge_styles_mapping(edge: dict):
               ...
           w.edge_styles_mapping = custom_edge_styles_mapping

        Returns
        -------
        None
        """
        self._edge_styles_mapping = edge_styles_mapping

    def get_edge_styles_mapping(self) -> Optional[Union[str, Callable[[dict], EdgeStyle]]]:
        """Legacy getter for edge_styles_mapping.

        Deprecated, use ``widget.edge_styles_mapping`` instead.
        """
        warnings.warn(
            "get_edge_styles_mapping() is deprecated; use `widget.edge_styles_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.edge_styles_mapping

    def set_edge_styles_mapping(self, edge_styles_mapping: Optional[Union[str, Callable[[dict], EdgeStyle]]]) -> None:
        """Legacy setter for edge_styles_mapping.

        Deprecated, use ``widget.edge_styles_mapping = value`` instead.
        """
        warnings.warn(
            "set_edge_styles_mapping() is deprecated; use `widget.edge_styles_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edge_styles_mapping = edge_styles_mapping

    def del_edge_styles_mapping(self) -> None:
        """Legacy deleter for edge_styles_mapping.

        Deprecated, use ``widget.edge_styles_mapping = None`` instead.
        """
        warnings.warn(
            "del_edge_styles_mapping() is deprecated; use `widget.edge_styles_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edge_styles_mapping = None
    # endregion

    # region edge_thickness_factor_mapping
    @property
    def edge_thickness_factor_mapping(self) -> Optional[Union[str, Callable[[dict], float]]]:
        """Getter for the edge thickness factor mapping property.

        Returns
        -------
        edge_thickness_factor_mapping: callable | str | None
            A function that produces edge thickness factors or the name of the property to use for the thickness binding,
            or ``None`` if no mapping is currently set.
        """
        return self._edge_thickness_factor_mapping

    @edge_thickness_factor_mapping.setter
    def edge_thickness_factor_mapping(self, edge_thickness_factor_mapping: Optional[Union[str, Callable[[dict], float]]]) -> None:
        """Setter for the edge thickness factor mapping property.

        Parameters
        ----------
        edge_thickness_factor_mapping: callable | str | None
            A function that produces edge thickness factors or the name of the property to use for the thickness binding.
            The function should have the same signature as `default_edge_thickness_factor_mapping`,
            e.g., take in an edge dictionary and return a positive float.
            If ``None`` is passed, this unsets the mapping.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_edge_thickness_factor_mapping(edge: dict):
               ...
           w.edge_thickness_factor_mapping = custom_edge_thickness_factor_mapping

        Returns
        -------
        None
        """
        self._edge_thickness_factor_mapping = edge_thickness_factor_mapping

    def get_edge_thickness_factor_mapping(self) -> Optional[Union[str, Callable[[dict], float]]]:
        """Legacy getter for edge_thickness_factor_mapping.

        Deprecated, use ``widget.edge_thickness_factor_mapping`` instead.
        """
        warnings.warn(
            "get_edge_thickness_factor_mapping() is deprecated; use `widget.edge_thickness_factor_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.edge_thickness_factor_mapping

    def set_edge_thickness_factor_mapping(
            self, edge_thickness_factor_mapping: Optional[Union[str, Callable[[dict], float]]]
    ) -> None:
        """Legacy setter for edge_thickness_factor_mapping.

        Deprecated, use ``widget.edge_thickness_factor_mapping = value`` instead.
        """
        warnings.warn(
            "set_edge_thickness_factor_mapping() is deprecated; use `widget.edge_thickness_factor_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edge_thickness_factor_mapping = edge_thickness_factor_mapping

    def del_edge_thickness_factor_mapping(self) -> None:
        """Legacy deleter for edge_thickness_factor_mapping.

        Deprecated, use ``widget.edge_thickness_factor_mapping = None`` instead.
        """
        warnings.warn(
            "del_edge_thickness_factor_mapping() is deprecated; use `widget.edge_thickness_factor_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.edge_thickness_factor_mapping = None
    # endregion

    # region directed_mapping
    @property
    def directed_mapping(self) -> Optional[Union[str, Callable[[dict], bool]]]:
        """Getter for the edge direction mapping property.

        Returns
        -------
        directed_mapping: callable | str | None
            A function that produces edge directions or the name of the property to use for the direction binding,
            or ``None`` if no mapping is currently set.
        """
        return self._directed_mapping

    @directed_mapping.setter
    def directed_mapping(self, directed_mapping: Optional[Union[str, Callable[[dict], bool]]]) -> None:
        """Setter for the edge direction mapping property.

        Parameters
        ----------
        directed_mapping: callable | str | None
            A function that produces edge directions or the name of the property to use for the direction binding.
            The function should have the same signature as `default_directed_mapping`,
            e.g., take in an edge dictionary and return a boolean value.
            If ``None`` is passed, this unsets the mapping.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget()
           def custom_directed_mapping(edge: dict):
               ...
           w.directed_mapping = custom_directed_mapping

        Returns
        -------
        None
        """
        self._directed_mapping = directed_mapping

    def get_directed_mapping(self) -> Optional[Union[str, Callable[[dict], bool]]]:
        """Legacy getter for directed_mapping.

        Deprecated, use ``widget.directed_mapping`` instead.
        """
        warnings.warn(
            "get_directed_mapping() is deprecated; use `widget.directed_mapping` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.directed_mapping

    def set_directed_mapping(self, directed_mapping: Optional[Union[str, Callable[[dict], bool]]]) -> None:
        """Legacy setter for directed_mapping.

        Deprecated, use ``widget.directed_mapping = value`` instead.
        """
        warnings.warn(
            "set_directed_mapping() is deprecated; use `widget.directed_mapping = value` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.directed_mapping = directed_mapping

    def del_directed_mapping(self) -> None:
        """Legacy deleter for directed_mapping.

        Deprecated, use ``widget.directed_mapping = None`` instead.
        """
        warnings.warn(
            "del_directed_mapping() is deprecated; use `widget.directed_mapping = None` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.directed_mapping = None
    # endregion

    # endregion Edge Mappings

    # endregion Data Mappings

    # region Default Mappings

    @staticmethod
    def default_element_property_mapping(index: int, element: TDict):
        """The default property mapping for graph elements.

        Simply selects the properties value of element dictionary.

        Parameters
        ----------
        index: int (optional)
        element: Dict

        Notes
        -----
        This is the default value for the {`node|edge`}_property_mapping property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_element_property_mapping(element: Dict):
           ...
           w.set_{node|edge}_property_mapping(custom_element_property_mapping)

        Returns
        -------
        properties: Dict

        """
        return element.get('properties', {})

    @staticmethod
    def default_node_property_mapping(index: int, node: TDict):
        """See default element property mapping."""
        return GraphWidget.default_element_property_mapping(index, node)

    @staticmethod
    def default_edge_property_mapping(index: int, edge: TDict):
        """See default element property mapping."""
        return GraphWidget.default_element_property_mapping(index, edge)

    def default_element_label_mapping(self, index: int, element: TDict):
        """The default label mapping for graph elements.

        Element (dict) should have key properties which itself should be a dict.
        Then one of the following values (in descending priority) is used as label if the label is a string:

        - properties["label"]
        - properties["yf_label"]

        When importing a Neo4j graph, the following properties are values are used as labels (in descending priority):

        - properties['name']
        - properties['title']
        - properties['label']
        - properties['description']
        - properties['caption']
        - properties['text']

        Parameters
        ----------
        index: int (optional)
        element: Dict

        Notes
        -----
        This is the default value for the {`node|edge`}_label_mapping property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        When a string is provided as the function argument, the key will be searched for in both the properties
        dictionary and the element keys.

        Example
        -------

        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           w.{node|edge}_label_mapping = 'id'

        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_element_label_mapping(element: Dict):
           ...
           w.set_{node|edge}_label_mapping(custom_element_label_mapping)

        Returns
        -------
        label: str

        """
        properties = element.get('properties', {})
        item_label = str(properties.get('label', properties.get('yf_label', '')))
        if self._data_importer == 'neo4j':
            item_label = get_neo4j_item_text(element) or item_label

        return item_label

    def default_node_label_mapping(self, index: int, node: TDict):
        """See default element label mapping."""
        return self.default_element_label_mapping(index, node)

    def default_edge_label_mapping(self, index: int, edge: TDict):
        """See default element label mapping."""
        return self.default_element_label_mapping(index, edge)

    def default_neo4j_color_mapping(self, index: int, element: TDict):
        itemtype = element['properties']['label']
        if itemtype not in self._itemtype2colorIdx:
            self._itemtype2colorIdx[itemtype] = len(self._itemtype2colorIdx)

        color_index = self._itemtype2colorIdx[itemtype] % len(COLOR_PALETTE)
        return COLOR_PALETTE[color_index]

    def default_node_color_mapping(self, index: int, node: TDict):
        """The default color mapping for nodes.

        Provides constant value of '#15AFAC' for all nodes, or different colors per label/type when importing a Neo4j
        graph.

        Parameters
        ----------
        index: int (optional)
        node: Dict

        Notes
        -----
        This is the default value for the `node_color_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_color_mapping(node: Dict):
           ...
           w.set_node_color_mapping(custom_node_color_mapping)

        Returns
        -------
        color: str
            css color value

        References
        ----------
        css color value <https://developer.mozilla.org/en-US/docs/Web/CSS/color_value>

        yFiles docs Fill api <https://docs.yworks.com/yfileshtml/#/api/Fill>

        """
        if self._data_importer == 'neo4j':
            return self.default_neo4j_color_mapping(index, node)
        else:
            return '#15AFAC'

    @staticmethod
    def default_node_styles_mapping(index: int, node: TDict):
        """The default styles mapping for nodes.

        Parameters
        ----------
        index: int (optional)
        node: Dict

        Notes
        -----
        This is the default value for the `node_styles_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_styles_mapping(node: Dict):
           ...
           w.set_node_styles_mapping(custom_node_styles_mapping)

        Returns
        -------

        styles: Dict
            can contain the following key-value-pairs:
                "color": str
                    CSS color value.
                "shape": str
                    The shape of the node. Possible values: 'ellipse', 'hexagon', 'hexagon2', 'octagon', 'pill', 'rectangle', 'round-rectangle' or 'triangle'.
                "image": str
                    Url or data URL of the image.

        References
        ----------
        css color value <https://developer.mozilla.org/en-US/docs/Web/CSS/color_value>

        Data URL <https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URLs>

        """
        return {}

    @staticmethod
    def default_edge_styles_mapping(index: int, edge: TDict):
        """The default styles mapping for edges.

        Parameters
        ----------
        index: int (optional)
        edge: Dict

        Notes
        -----
        This is the default value for the `edge_styles_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_edge_styles_mapping(edge: Dict):
           ...
           w.set_edge_styles_mapping(custom_edge_styles_mapping)

        Returns
        -------
        A dict containing styling properties for edges.
        Can contain the following key-value-pairs:
            "color": str
                CSS color value.
            "directed": bool
                Whether the edge should be visualized with a target arrow.
            "thickness": float
                The stroke thickness of the edge.
            "dashStyle": dict
                The dash styling of the edge. Can be one of the following strings:
                    - "solid"
                    - "dash"
                    - "dot"
                    - "dash-dot"
                    - "dash-dot-dot"
                    - "5 10"
                    - "5, 10"
                    - ...

        References
        ----------

        Data URL https://docs.yworks.com/yfileshtml/#/api/DashStyle

        """
        return {}

    @staticmethod
    def default_node_label_style_mapping(index: int, node: TDict):
        return {}

    def default_edge_color_mapping(self, index: int, edge: TDict):
        """The default color mapping for edges.

        Provides constant value of '#15AFAC' for all edges.

        Parameters
        ----------
        index: int (optional)
        edge: Dict

        Notes
        -----
        This is the default value for the `edge_color_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_edge_color_mapping(edge: Dict):
           ...
           w.set_edge_color_mapping(custom_edge_color_mapping)

        Returns
        -------
        color: str
            css color value

        References
        ----------
        css color value <https://developer.mozilla.org/en-US/docs/Web/CSS/color_value>

        yFiles docs Fill api <https://docs.yworks.com/yfileshtml/#/api/Fill>

        """
        if self._data_importer == 'neo4j':
            return self.default_neo4j_color_mapping(index, edge)
        else:
            return '#15AFAC'

    @staticmethod
    def default_node_scale_factor_mapping(index: int, node: TDict):
        """The default scale factor mapping for nodes.

        Provides constant value of 1.0 for all nodes.

        Parameters
        ----------
        index: int (optional)
        node: Dict

        Notes
        -----
        This is the default value for the `node_scale_factor_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_scale_factor_mapping(node: Dict):
           ...
           w.set_node_scale_factor_mapping(custom_node_scale_factor_mapping)

        Returns
        -------
        node_scale_factor: float

        """
        return 1.0

    @staticmethod
    def default_heat_mapping(element: TDict):
        """The default scale factor mapping for nodes.

                Provides constant value of None for all elements.

                Parameters
                ----------
                element: Dict

                Notes
                -----
                This is the default value for the `heat_mapping` property.
                Can be 'overwritten' by setting the property
                with a function of the same signature.

                If the given mapping function has only one parameter (that is not typed as int),
                then it will be called with the element (Dict) as first parameter.

                Example
                -------
                .. code::

                   from yfiles_graphs_for_streamlit import StreamlitGraphWidget
                   w = StreamlitGraphWidget
                   def custom_heat_mapping(element: Dict):
                   ...
                   w.set_heat_mapping(custom_heat_mapping)

                Returns
                -------
                heat: float | None

                """
        return None

    @staticmethod
    def default_node_size_mapping(index: int, node: TDict):
        """The default size mapping for nodes.

                Provides constant value 55.0, 55.0 for the width and height of all nodes.

                Parameters
                ----------
                index: int (optional)
                node: Dict

                Notes
                -----
                This is the default value for the `node_size_mapping` property.
                Can be 'overwritten' by setting the property
                with a function of the same signature.

                If the given mapping function has only one parameter (that is not typed as int),
                then it will be called with the element (Dict) as first parameter.

                Example
                -------
                .. code::

                   from yfiles_graphs_for_streamlit import StreamlitGraphWidget
                   w = StreamlitGraphWidget
                   def custom_node_size_mapping(node: Dict):
                   ...
                   w.set_node_size_mapping(custom_node_size_mapping)

                Returns
                -------
                size: float 2-tuple

                """
        return 55.0, 55.0

    @staticmethod
    def default_node_layout_mapping(index: int, node: TDict):
        """The default layout mapping for nodes.

                Provides constant value None for all nodes.
                Position and size mappings are used instead.
                Default position and size mappings are a constant value of 0.0, 0.0, and 55.0,55.0 respectively.

                Parameters
                ----------
                index: int (optional)
                node: Dict

                Notes
                -----
                This is the default value for the `node_layout_mapping` property.
                Can be 'overwritten' by setting the property
                with a function returning a float 4-tuple.

                The layout overwrites position and size mappings if not None.

                If the given mapping function has only one parameter (that is not typed as int),
                then it will be called with the element (Dict) as first parameter.

                Example
                -------
                .. code::

                   from yfiles_graphs_for_streamlit import StreamlitGraphWidget
                   w = StreamlitGraphWidget
                   def custom_node_layout_mapping(node: Dict):
                   ...
                   w.set_node_layout_mapping(custom_node_layout_mapping)

                Returns
                -------
                layout: None | float 4-tuple

                """
        return None

    @staticmethod
    def default_edge_thickness_factor_mapping(index: int, edge: TDict):
        """The default thickness factor mapping for edges.

        Provides constant value of 1.0 for all edges.

        Parameters
        ----------
        index: int (optional)
        edge: Dict

        Notes
        -----
        This is the default value for the `edge_thickness_factor_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_edge_thickness_factor_mapping(edge: Dict):
           ...
           w.set_edge_thickness_factor_mapping(custom_edge_thickness_factor_mapping)

        Returns
        -------
        edge_thickness_factor: float

        """
        return 1.0

    @staticmethod
    def default_node_type_mapping(index: int, node: TDict):
        """The default type mapping for nodes.

        Provides the mapped node color to distinguish different node types

        Parameters
        ----------
        index: int (optional)
        node: Dict

        Notes
        -----
        This is the default value for the `node_type_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_type_mapping(node: Dict):
           ...
           w.set_node_type_mapping(custom_node_type_mapping)

        Returns
        -------
        type: None

        """
        if 'color' in node:
            return node['color']
        else:
            return None

    @staticmethod
    def default_node_parent_mapping(index: int, node: TDict):
        """The default parent mapping for nodes.

        Provides constant value None for all nodes

        Parameters
        ----------
        index: int (optional)
        node: Dict

        Notes
        -----
        This is the default value for the `node_parent_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_parent_mapping(node: Dict):
           ...
           w.set_node_parent_mapping(custom_node_parent_mapping)

        Returns
        -------
        parent: None

        """
        return None

    @staticmethod
    def default_node_parent_group_mapping(index: int, node: TDict):
        """The default parent mapping for nodes.

        Provides constant value None for all nodes

        Parameters
        ----------
        index: int (optional)
        node: Dict

        Notes
        -----
        This is the default value for the `node_parent_group_mapping` property.
        Can be 'overwritten' by setting the `node_parent_group_mapping` property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_parent_group_mapping(node: Dict):
           ...
           w.set_node_parent_group_mapping(custom_node_parent_group_mapping)

        Returns
        -------
        parent: None

        """
        return None

    @staticmethod
    def default_node_position_mapping(index: int, node: TDict):
        """The default position mapping for nodes.

        Provides constant value of 0.0, 0.0 for all nodes.

        Parameters
        ----------
        index: int (optional)
        node: Dict

        Notes
        -----
        This is the default value for the `node_position_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_position_mapping(node: Dict):
           ...
           w.set_node_position_mapping(custom_node_position_mapping)

        Returns
        -------
        position: float 2-tuple

        """
        return 0.0, 0.0

    @staticmethod
    def default_node_coordinate_mapping(index: int, node: TDict):
        """The default coordinate mapping for nodes.

        Provides constant value of None for all nodes.

        Parameters
        ----------
        index: int (optional)
        node: Dict

        Notes
        -----
        This is the default value for the `node_coordinate_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_node_coordinate_mapping(node: Dict):
           ...
           w.set_node_coordinate_mapping(custom_node_coordinate_mapping)

        Returns
        -------
        coordinate: float 2-tuple

        """
        return None

    def default_directed_mapping(self, index: int, edge: TDict):
        """The default directed mapping for edges.

        Uses the graph wide directed attribute for all edges.

        Parameters
        ----------
        index: int (optional)
        edge: Dict

        Notes
        -----
        This is the default value for the `directed_mapping` property.
        Can be 'overwritten' by setting the property
        with a function of the same signature.

        If the given mapping function has only one parameter (that is not typed as int),
        then it will be called with the element (Dict) as first parameter.

        Example
        -------
        .. code::

           from yfiles_graphs_for_streamlit import StreamlitGraphWidget
           w = StreamlitGraphWidget
           def custom_directed_mapping(edge: Dict):
           ...
           w.set_directed_mapping(custom_directed_mapping)

        Returns
        -------
        directed: bool

        """
        return self._directed
    # endregion


    def import_graph(self, graph):
        """Import a graph object defined in an external module.

        Sets the nodes, edges, and directed properties
        with information extracted from the graph object.
        See yfiles_jupyter_graphs.graph.importer for object specific transformation details.

        Parameters
        ----------
        graph: networkx.{Multi}{Di}Graph | graph_tool.Graph | igraph.Graph | pygraphviz.AGraph | neo4j.graph.Subgraph
            graph data structure

        Example
        -------
        .. code::

            from networkx import florentine_families_graph
            from yfiles_graphs_for_streamlit import StreamlitGraphWidget
            w = StreamlitGraphWidget
            w.import_graph(florentine_families_graph())

        Notes
        -----
        Some graph data structures have special attributes for labels, some don't.
        Same goes for other graph properties.
        This method and the underlying transformations should be seen as best effort
        to provide an easy way to input data into the widget.
        For more granular control use nodes and edges properties directly.

        Returns
        -------

        """
        self._nodes, self._edges, self._directed, self._data_importer = import_(graph)

    # region Public Layouts

    def map_layout(self):
        """Alias for self.set_graph_layout(algorithm="map").

        Uses geo-coordinates and a map background to visualize the graph.
        """
        self.graph_layout = Layout.MAP

    def interactive_organic_layout(self):
        """Alias for self.set_graph_layout(algorithm="interactive_organic").

        See yFiles interactive organic layout guide
        <https://docs.yworks.com/yfileshtml/#/dguide/organic_layout#interactive_organic_layout>
        for more details about this specific algorithm.
        """
        self.graph_layout = Layout.INTERACTIVE_ORGANIC

    def circular_layout(self):
        """Alias for self.set_graph_layout(algorithm="circular").

        See yFiles circular layout guide
        <https://docs.yworks.com/yfileshtml/#/dguide/layout-summary#layout_styles-circular>
        for more details about this specific algorithm.
        """
        self.graph_layout = Layout.CIRCULAR

    def circular_straight_line_layout(self):
        """Alias for self.set_graph_layout(algorithm="circular_straight_line").

        Similar to circular layout but with straight edge paths instead of bundled paths.

        See yFiles circular layout guide
        <https://docs.yworks.com/yfileshtml/#/dguide/layout-summary#layout_styles-circular>
        for more details about this specific algorithm.
        """
        self.graph_layout = Layout.CIRCULAR_STRAIGHT_LINE

    def hierarchic_layout(self):
        """Alias for self.set_graph_layout(algorithm="hierarchic").

        See yFiles hierarchic layout guide
        <https://docs.yworks.com/yfileshtml/#/dguide/layout-summary#layout_styles-hierarchical>
        for more details about this specific algorithm.
        """
        self.graph_layout = Layout.HIERARCHIC

    def organic_layout(self):
        """Alias for self.set_graph_layout(algorithm="organic").

        See yFiles organic layout guide
        <https://docs.yworks.com/yfileshtml/#/dguide/layout-summary#layout_styles-organic>
        for more details about this specific algorithm.
        """
        self.graph_layout = Layout.ORGANIC

    def orthogonal_layout(self):
        """Alias for self.set_graph_layout(algorithm="orthogonal").

        See yFiles orthogonal layout guide
        <https://docs.yworks.com/yfileshtml/#/dguide/layout-summary#layout_styles-orthogonal>
        for more details about this specific algorithm.
        """
        self.graph_layout = Layout.ORTHOGONAL

    def radial_layout(self):
        """Alias for self.set_graph_layout(algorithm="radial").

        See yFiles radial layout guide
        <https://docs.yworks.com/yfileshtml/#/dguide/layout-summary#layout_styles-radial>
        for more details about this specific algorithm.
        """
        self.graph_layout = Layout.RADIAL

    def tree_layout(self):
        """Alias for self.set_graph_layout(algorithm="tree").

        See yFiles tree layout guide
        <https://docs.yworks.com/yfileshtml/#/dguide/layout-summary#layout_styles-tree>
        for more details about this specific algorithm.
        """
        self.graph_layout = Layout.TREE

    def orthogonal_edge_router(self):
        """Alias for self.set_graph_layout(algorithm="orthogonal_edge_router").

        See yFiles orthogonal edge router guide
        <https://docs.yworks.com/yfileshtml/#/dguide/layout-summary#layout_styles-polyline_router>
        for more details about this specific algorithm.
        """
        self.graph_layout = Layout.ORTHOGONAL_EDGE_ROUTER

    def organic_edge_router(self):
        """Alias for self.set_graph_layout(algorithm="organic_edge_router").

        See yFiles organic edge router guide
        <https://docs.yworks.com/yfileshtml/#/dguide/layout-summary#layout_styles-organic_router>
        for more details about this specific algorithm.
        """
        self.graph_layout = Layout.ORGANIC_EDGE_ROUTER

    def no_layout(self):
        """Alias for self.set_graph_layout(algorithm="no_layout").

        No layout algorithm is applied.

        """
        self.graph_layout = Layout.NO_LAYOUT

    # endregion
