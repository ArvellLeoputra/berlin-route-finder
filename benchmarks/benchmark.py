import time
import osmnx as ox
from routing import find_route, build_index
from benchmarks.timing import best_time

routes = {
    "Brandenburger Tor → Potsdamer Platz": ((52.5163, 13.3777), (52.5096, 13.3760)),
    "Hauptbahnhof → Alexanderplatz": ((52.5251, 13.3694), (52.5219, 13.4132)),
    "Zoologischer Garten → East Side Gallery": ((52.5070, 13.3324), (52.5050, 13.4397)),
}

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

# time the search only: nearest intersections + shortest path
G, index = graphs["walk"]
print(f"\n{'Walking route':<42}{'Distance':>10}{'Without index':>16}{'With index':>13}")
for name, (start, end) in routes.items():
    t_old, distance = best_time(G, start, end)
    t_new, _ = best_time(G, start, end, index=index)
    print(f"{name:<42}{distance:>8.0f} m{t_old:>14.3f} s{t_new:>11.3f} s")