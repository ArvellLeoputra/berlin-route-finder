"""
Time the startup (loading graphs, building the index) and searches with and without the prebuilt index
"""

import time

import osmnx as ox

from benchmarks.routes import ROUTES
from benchmarks.timing import best_time
from src.routing import build_index

graphs = {}
print("Startup (once)")
for mode in ("walk", "bike"):
    t0 = time.perf_counter()
    G = ox.load_graphml(f"data/{mode}.graphml.gz")
    t1 = time.perf_counter()
    index = build_index(G)
    t2 = time.perf_counter()
    graphs[mode] = (G, index)
    print(f"  {mode:<5}{len(G.nodes):>7,} intersections   "
          f"load {t1 - t0:.1f} s   index {t2 - t1:.2f} s")

# Time the search only: nearest intersections + shortest path
for mode in ("walk", "bike"):
    G, index = graphs[mode]
    label = "Walking route" if mode == "walk" else "Cycling route"
    print(f"\n{label:<42}{'Distance':>10}{'Without index':>16}{'With index':>13}")
    for name, (start, end) in ROUTES.items():
        t_old, distance = best_time(G, start, end)
        t_new, _ = best_time(G, start, end, index=index)
        print(f"{name:<42}{distance:>8.0f} m{t_old:>14.3f} s{t_new:>11.3f} s")
