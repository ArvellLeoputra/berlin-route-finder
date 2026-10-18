import time
import osmnx as ox
from routing import load_graph, find_route

# skip OSMnx saved downloads
ox.settings.use_cache = False

routes = {
    "Brandenburger Tor → Potsdamer Platz": ((52.5163, 13.3777), (52.5096, 13.3760)),
    "Hauptbahnhof → Alexanderplatz": ((52.5251, 13.3694), (52.5219, 13.4132)),
    "Zoologischer Garten → East Side Gallery": ((52.5070, 13.3324), (52.5050, 13.4397)),
}

for name, (start, end) in routes.items():
    t0 = time.perf_counter()
    G = load_graph(start, end)
    t1 = time.perf_counter()
    route, distance = find_route(G, start, end)
    t2 = time.perf_counter()
    print(f"{name}: {distance:.0f} m, {t1 - t0:.3f} s (load), {t2 - t1:.3f} s (find)")
    time.sleep(10)  # pause between requests