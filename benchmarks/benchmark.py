import time
import osmnx as ox
from routing import find_route

routes = {
    "Brandenburger Tor → Potsdamer Platz": ((52.5163, 13.3777), (52.5096, 13.3760)),
    "Hauptbahnhof → Alexanderplatz": ((52.5251, 13.3694), (52.5219, 13.4132)),
    "Zoologischer Garten → East Side Gallery": ((52.5070, 13.3324), (52.5050, 13.4397)),
}

t0 = time.perf_counter()
G = ox.load_graphml("data/walk.graphml.gz")
t1 = time.perf_counter()
print(f"Load graph:  {t1 - t0:.1f} s")

for name, (start, end) in routes.items():
    times = []
    for _ in range(5):
        t0 = time.perf_counter()
        route, distance = find_route(G, start, end)
        times.append(time.perf_counter() - t0)
    print(f"{name}: {distance:.0f} m, {min(times):.3f} s")