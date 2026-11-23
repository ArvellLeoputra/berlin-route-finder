"""
Time the shortlist planner with different shortlist sizes and numbers of errands
"""
import math

import osmnx as ox

from src.planner import load_shops, plan_trip
from src.routing import build_index
from benchmarks.routes import UNI, HOME
from benchmarks.timing import timed_plan

KINDS = ["Post office", "Pharmacy", "Groceries", "Bakery", "ATM", "Drugstore"]

G = ox.load_graphml("data/walk.graphml.gz")
index = build_index(G)
shops = load_shops()


def run(kinds, k):
    return timed_plan(plan_trip, G, index, UNI, HOME, shops, kinds, k=k)


# Compare number of shops per kind (3,5,8,10)
print("Shortlist size, 3 errands")
print(f"{'Shortlist':>9}{'Possible trips':>16}{'Distance':>11}{'Time':>9}   Stops")
for k in (3, 5, 8, 10):
    stops, distance, seconds = run(KINDS[:3], k)
    names = ", ".join(s.name or s.kind for s in stops)
    print(f"{k:>9}{k ** 3 * 6:>16,}{distance / 1000:>9.2f} km{seconds:>7.2f} s   {names}")

# Compare number of errands (1-6)
print("\nNumber of errands, 5 shops per kind")
print(f"{'Errands':>9}{'Possible trips':>16}{'Distance':>11}{'Time':>9}")
for n in range(1, len(KINDS) + 1):
    stops, distance, seconds = run(KINDS[:n], 5)
    trips = 5 ** n * math.factorial(n)
    print(f"{n:>9}{trips:>16,}{distance / 1000:>9.2f} km{seconds:>7.2f} s")
