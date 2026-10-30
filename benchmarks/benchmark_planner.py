import math
import time

import osmnx as ox

from src.planner import load_shops, plan_trip
from src.routing import build_index

UNI = (52.5125, 13.3269)    # TU Berlin
HOME = (52.5219, 13.4132)   # Alexanderplatz
KINDS = ["Post office", "Pharmacy", "Groceries", "Bakery", "ATM", "Drugstore"]

G = ox.load_graphml("data/walk.graphml.gz")
index = build_index(G)
shops = load_shops()


def run(kinds, k):
    t0 = time.perf_counter()
    stops, distance, _ = plan_trip(G, index, UNI, HOME, shops, kinds, k=k)
    return distance, time.perf_counter() - t0, stops


# 1) Bigger shortlists are slower but less likely to miss the best shop (3 errands)
print("Shortlist size, 3 errands")
print(f"{'Shortlist':>9}{'Possible trips':>16}{'Distance':>11}{'Time':>9}   Stops")
for k in (3, 5, 8, 10):
    distance, seconds, stops = run(KINDS[:3], k)
    names = ", ".join(s.name or s.kind for s in stops)
    print(f"{k:>9}{k ** 3 * 6:>16,}{distance / 1000:>9.2f} km{seconds:>7.2f} s   {names}")

# 2) More errands (5 shops per kind)
print("\nNumber of errands, 5 shops per kind")
print(f"{'Errands':>9}{'Possible trips':>16}{'Distance':>11}{'Time':>9}")
for n in range(1, len(KINDS) + 1):
    distance, seconds, _ = run(KINDS[:n], 5)
    trips = 5 ** n * math.factorial(n)
    print(f"{n:>9}{trips:>16,}{distance / 1000:>9.2f} km{seconds:>7.2f} s")