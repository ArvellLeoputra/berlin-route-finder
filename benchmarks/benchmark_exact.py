import random
import statistics
import time

import networkx as nx
import osmnx as ox

from src.config import CENTER
from src.exact import plan_trip_exact
from src.planner import load_shops, plan_trip
from src.routing import build_index

TRIPS = 40           # random start/end pairs per test
MIN_DISTANCE = 1500  # skip pairs closer than this (m), they're too easy
KINDS = ["Post office", "Pharmacy", "Groceries", "Bakery", "ATM", "Drugstore"]

G = ox.load_graphml("data/walk.graphml.gz")
index = build_index(G)
shops = load_shops()

# Random start and end points inside the covered area, the same ones for every test
random.seed(7)
nodes = [n for n in G.nodes
         if ox.distance.great_circle(CENTER[0], CENTER[1], G.nodes[n]["y"], G.nodes[n]["x"]) < 4000]
pairs = []
while len(pairs) < TRIPS:
    a, b = random.sample(nodes, 2)
    start, end = (G.nodes[a]["y"], G.nodes[a]["x"]), (G.nodes[b]["y"], G.nodes[b]["x"])
    if ox.distance.great_circle(*start, *end) >= MIN_DISTANCE:
        pairs.append((start, end))


def timed(planner, *args, **kwargs):
    t0 = time.perf_counter()
    _, distance, _ = planner(*args, **kwargs)
    return distance, time.perf_counter() - t0


for n in (3, 6):
    kinds = KINDS[:n]
    results = []
    for start, end in pairs:
        try:
            exact, t_exact = timed(plan_trip_exact, G, index, start, end, shops, kinds)
            short, t_short = timed(plan_trip, G, index, start, end, shops, kinds, k=5)
        except nx.NetworkXNoPath:
            continue
        results.append((exact, short, t_exact, t_short))

    missed = [s - e for e, s, _, _ in results if s - e > 0.5]
    print(f"\n{n} errands, {len(results)} random trips")
    print(f"  Shortlist finds the best trip:  {len(results) - len(missed)} of {len(results)}")
    if missed:
        print(f"  When it misses, longer by:      {statistics.mean(missed):.0f} m on average, {max(missed):.0f} m at most")
    print(f"  Average extra distance:         {100 * statistics.mean((s - e) / e for e, s, _, _ in results):.1f} %")
    print(f"  Time, exact (mean / max):       {statistics.mean(r[2] for r in results):.2f} s / {max(r[2] for r in results):.2f} s")
    print(f"  Time, shortlist (mean / max):   {statistics.mean(r[3] for r in results):.2f} s / {max(r[3] for r in results):.2f} s")