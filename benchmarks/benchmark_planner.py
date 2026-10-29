import time

import osmnx as ox

from src.planner import load_shops, plan_trip
from src.routing import build_index

UNI = (52.5125, 13.3269)    # TU Berlin
HOME = (52.5219, 13.4132)   # Alexanderplatz
KINDS = ["Post office", "Pharmacy", "Groceries"]

G = ox.load_graphml("data/walk.graphml.gz")
index = build_index(G)
shops = load_shops()

# Bigger shortlists are slower but less likely to miss the best shop
print(f"{'Shortlist':>9}{'Trips tried':>13}{'Distance':>11}{'Time':>9}   Stops")
for k in (3, 5, 8, 10):
    t0 = time.perf_counter()
    stops, distance, _ = plan_trip(G, index, UNI, HOME, shops, KINDS, k=k)
    seconds = time.perf_counter() - t0
    names = ", ".join(s.name or s.kind for s in stops)
    print(f"{k:>9}{k ** len(KINDS) * 6:>13,}{distance / 1000:>9.2f} km{seconds:>7.2f} s   {names}")