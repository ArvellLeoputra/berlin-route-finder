"""
Time searches on the first version: streets downloaded live from the Overpass API for every route
"""
import time
import osmnx as ox

from src.routing import load_graph, find_route
from benchmarks.routes import ROUTES

# skip OSMnx saved downloads
ox.settings.use_cache = False

for name, (start, end) in ROUTES.items():
    t0 = time.perf_counter()
    G = load_graph(start, end)
    t1 = time.perf_counter()
    route, distance = find_route(G, start, end)
    t2 = time.perf_counter()
    print(f"{name}: {distance:.0f} m, {t1 - t0:.3f} s (load), {t2 - t1:.3f} s (find)")
    time.sleep(10)  # pause between requests
