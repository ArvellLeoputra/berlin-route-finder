import math

import osmnx as ox

from src.routing import build_index
from benchmarks.timing import best_time

routes = {
    "Brandenburger Tor → Potsdamer Platz": ((52.5163, 13.3777), (52.5096, 13.3760)),
    "Hauptbahnhof → Alexanderplatz": ((52.5251, 13.3694), (52.5219, 13.4132)),
    "Zoologischer Garten → East Side Gallery": ((52.5070, 13.3324), (52.5050, 13.4397)),
}

G = ox.load_graphml("data/walk.graphml.gz")
index = build_index(G)

print(f"{'Walking route':<42}{'Distance':>10}{'Bidirectional':>15}{'A*':>10}{'Speedup':>9}")
for name, (start, end) in routes.items():
    t_bidirectional, d_bidirectional = best_time(G, start, end, index=index)
    t_astar, d_astar = best_time(G, start, end, index=index, algorithm="astar")
    assert math.isclose(d_bidirectional, d_astar, rel_tol=1e-6), "A* and bidirectional search disagree"
    print(f"{name:<42}{d_bidirectional:>8.0f} m{t_bidirectional:>13.3f} s{t_astar:>8.3f} s{t_bidirectional / t_astar:>8.1f}×")