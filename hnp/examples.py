from __future__ import annotations

from math import sqrt

from hnp.embedding import Point
from hnp.graph import Graph


def moser_spindle() -> Graph:
    vertices = ("x", "a", "b", "y", "c", "d", "z")
    edges = (
        ("x", "a"),
        ("x", "b"),
        ("a", "b"),
        ("a", "y"),
        ("b", "y"),
        ("x", "c"),
        ("x", "d"),
        ("c", "d"),
        ("c", "z"),
        ("d", "z"),
        ("y", "z"),
    )
    return Graph.from_edges(vertices, edges)


def moser_spindle_coordinates() -> dict[str, Point]:
    root3 = sqrt(3.0)
    y = (root3, 0.0)
    z = (5.0 / (2.0 * root3), sqrt(11.0) / (2.0 * root3))

    midpoint = (z[0] / 2.0, z[1] / 2.0)
    perpendicular = (-z[1] / root3, z[0] / root3)
    c = (midpoint[0] + perpendicular[0] / 2.0, midpoint[1] + perpendicular[1] / 2.0)
    d = (midpoint[0] - perpendicular[0] / 2.0, midpoint[1] - perpendicular[1] / 2.0)

    return {
        "x": (0.0, 0.0),
        "a": (root3 / 2.0, 0.5),
        "b": (root3 / 2.0, -0.5),
        "y": y,
        "c": c,
        "d": d,
        "z": z,
    }
