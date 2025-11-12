def make_json_safe(obj, *, max_depth=20, decimals_as="str"):
    import decimal, math, pathlib, uuid
    from collections import abc

    try:
        import neo4j # type: ignore[import]
    except Exception:
        neo4j = None
    try:
        import networkx as nx # type: ignore[import]
    except Exception:
        nx = None
    try:
        import igraph as ig # type: ignore[import]
    except Exception:
        ig = None
    try:
        import rdflib # type: ignore[import]
    except Exception:
        rdflib = None

    def _is_primitive(x):
        return x is None or isinstance(x, (str, int, float, bool))

    def _convert(x, depth=0, path="$"):
        if _is_primitive(x):
            if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
                return None
            return x
        if depth > max_depth:
            return f"<max_depth:{type(x).__name__}>"

        # ---- datetime-like ----
        import datetime as dt
        if isinstance(x, (dt.datetime, dt.date, dt.time)):
            return x.isoformat()
        if isinstance(x, dt.timedelta):
            return x.total_seconds()

        # ---- Decimal, UUID, Path ----
        if isinstance(x, decimal.Decimal):
            return str(x) if decimals_as == "str" else float(x)
        if isinstance(x, uuid.UUID):
            return str(x)
        if isinstance(x, pathlib.Path):
            return str(x)

        # ---- bytes ----
        if isinstance(x, (bytes, bytearray, memoryview)):
            import base64
            return {"__type__": "bytes", "base64": base64.b64encode(x).decode("ascii")}

        # ---- Neo4j types ----
        if neo4j:
            from neo4j.graph import Node, Relationship, Path # type: ignore[import]
            from neo4j.spatial import Point # type: ignore[import]
            from neo4j.time import DateTime, Date, Time, Duration # type: ignore[import]
            if isinstance(x, Node):
                return {
                    "__type__": "Neo4jNode",
                    "id": x.id,
                    "labels": list(x.labels),
                    "properties": _convert(dict(x.items()), depth + 1, f"{path}.props"),
                }
            if isinstance(x, Relationship):
                return {
                    "__type__": "Neo4jRelationship",
                    "id": x.id,
                    "type": x.type,
                    "start": x.start_node.id,
                    "end": x.end_node.id,
                    "properties": _convert(dict(x.items()), depth + 1, f"{path}.props"),
                }
            if isinstance(x, Path):
                return {
                    "__type__": "Neo4jPath",
                    "nodes": [_convert(n, depth + 1, f"{path}.nodes") for n in x.nodes],
                    "relationships": [_convert(r, depth + 1, f"{path}.rels") for r in x.relationships],
                }
            if isinstance(x, Point):
                return {"__type__": "Neo4jPoint", "coordinates": list(x), "srid": getattr(x, "srid", None)}
            if isinstance(x, (DateTime, Date, Time)):
                return x.iso_format()
            if isinstance(x, Duration):
                return x.iso_format()

        # ---- networkx ----
        if nx and isinstance(x, (nx.Graph, nx.DiGraph)):
            return {
                "__type__": "NetworkXGraph",
                "directed": x.is_directed(),
                "nodes": list(x.nodes(data=True)),
                "edges": list(x.edges(data=True)),
            }

        # ---- igraph ----
        if ig and isinstance(x, ig.Graph):
            return {
                "__type__": "IGraph",
                "directed": x.is_directed(),
                "nodes": [{"id": v.index, **v.attributes()} for v in x.vs],
                "edges": [
                    {"source": e.source, "target": e.target, **e.attributes()}
                    for e in x.es
                ],
            }

        # ---- RDFLib ----
        if rdflib:
            from rdflib import URIRef, BNode, Literal # type: ignore[import]
            if isinstance(x, (URIRef, BNode, Literal)):
                return str(x)

        # ---- dataclass / dictlike / iterable fallbacks ----
        import dataclasses
        if dataclasses.is_dataclass(x):
            return _convert(dataclasses.asdict(x), depth + 1, path + ".dc")
        if isinstance(x, abc.Mapping):
            out = {}
            for k, v in x.items():
                key = str(k)
                out[key] = _convert(v, depth + 1, f"{path}.{key}")
            return out
        if isinstance(x, (set, frozenset)):
            return [_convert(v, depth + 1, f"{path}[{i}]") for i, v in enumerate(x)]

        # ---- custom / fallback ----
        if hasattr(x, "__dict__"):
            return _convert(vars(x), depth + 1, path + ".obj")

        return x

    return _convert(obj)
