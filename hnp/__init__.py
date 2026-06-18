"""Hadwiger-Nelson finite graph research helpers."""

from hnp.coloring import ColoringSearchResult, find_coloring, is_proper_coloring
from hnp.core_analysis import CoreEdgeUsage, analyze_core_edge_usage, variable_to_vertex_color
from hnp.dimacs import ColoringCnf, color_var, coloring_cnf, graph_from_dimacs_edge_text, to_dimacs
from hnp.graph import Edge, Graph
from hnp.sat import DimacsCnf, SatResult, parse_dimacs_cnf_text, solve_dimacs_cnf_text

__all__ = [
    "DimacsCnf",
    "ColoringCnf",
    "ColoringSearchResult",
    "CoreEdgeUsage",
    "Edge",
    "Graph",
    "SatResult",
    "color_var",
    "coloring_cnf",
    "find_coloring",
    "graph_from_dimacs_edge_text",
    "is_proper_coloring",
    "parse_dimacs_cnf_text",
    "solve_dimacs_cnf_text",
    "to_dimacs",
    "analyze_core_edge_usage",
    "variable_to_vertex_color",
]
