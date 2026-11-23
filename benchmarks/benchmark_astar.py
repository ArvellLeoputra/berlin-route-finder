"""
Compare bidirectional search with A* on the same routes, and check they give the same distance
"""
import math

import osmnx as ox

from src.routing import build_index
from benchmarks.routes import ROUTES
from benchmarks.timing import best_time

G = ox.load_graphml("data/walk.graphml.gz")
index = build_index(G)

print(f"{'Walking route':<42}{'Distance':>10}{'Bidirectional':>15}{'A*':>10}{'Speedup':>9}")
for name, (start, end) in ROUTES.items():
    t_bidirectional, d_bidirectional = best_time(G, start, end, index=index)
    t_astar, d_astar = best_time(G, start, end, index=index, algorithm="astar")
    assert math.isclose(d_bidirectional, d_astar, rel_tol=1e-6), "A* and bidirectional search disagree"
    print(f"{name:<42}{d_bidirectional:>8.0f} m{t_bidirectional:>13.3f} s{t_astar:>8.3f} s{t_bidirectional / t_astar:>8.1f}×")
