import csv
import itertools
from collections import namedtuple

import networkx as nx
import osmnx as ox

from src.routing import find_route

Shop = namedtuple("Shop", ["kind", "name", "lat", "lon"])


# Read the saved shops and group them by kind
def load_shops(path="data/shops.csv"):
    shops = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            shop = Shop(row["kind"], row["name"], float(row["lat"]), float(row["lon"]))
            shops.setdefault(shop.kind, []).append(shop)
    return shops


# Turn a place into (lat, lon)
def point(place):
    return (place.lat, place.lon) if isinstance(place, Shop) else place


# Calculate straight-line distance in meters between two places
def straight_line(a, b):
    (lat1, lon1), (lat2, lon2) = point(a), point(b)
    return ox.distance.great_circle(lat1, lon1, lat2, lon2)


# Create a shortlist of shop candidates to optimize
def shortlist(shops, start, end, k=5):
    # The k shops with the smallest detour on the way from start to end (in straight lines).
    def detour(shop):
        return straight_line(shop, start) + straight_line(shop, end)

    return sorted(shops, key=detour)[:k]


def plan_trip(G, index, start, end, shops, kinds, k=5):
    """
    Best trip from start to end that visits one shop of each kind.

    Shortlists k shops per kind, then finds the best choice and order among them.
    Returns (stops in visiting order, total distance in m, route as a list of graph nodes).
    """
    candidates = [shortlist(shops[kind], start, end, k) for kind in kinds]  # list of lists, one list per errand kind

    legs = {}  # walking routes, computed only once per pair of places

    def leg(a, b):
        if (a, b) not in legs:
            try:
                legs[a, b] = find_route(G, point(a), point(b), index=index, algorithm="astar")
            except nx.NetworkXNoPath:
                legs[a, b] = (None, float("inf"))
        return legs[(a, b)]

    # best_stops, best_distance = None, float("inf")

    # # Try every combination of shops
    # for choice in itertools.product(*candidates):
    #     # Try every order of visiting them
    #     for order in itertools.permutations(choice):
    #         trip = [start, *order, end]
    #         distance = sum(leg(a, b)[1] for a, b in zip(trip, trip[1:]))

    #         if distance < best_distance:
    #             best_stops, best_distance = list(order), distance

    # if best_stops is None:
    #     raise nx.NetworkXNoPath("No route found")

    best_stops, best_distance = best_trip(start, end, candidates, lambda a, b: leg(a, b)[1])

    # Join the legs of the best trip into one route for the map
    trip = [start, *best_stops, end]
    route = []
    for a, b in zip(trip, trip[1:]):
        nodes = leg(a, b)[0]
        route += nodes if not route else nodes[1:]  # don't repeat the shared node

    return best_stops, best_distance, route

 
def best_trip(start, end, candidates, dist):
    if not candidates:
        return [], dist(start, end)

    all_kinds = frozenset(range(len(candidates)))

    # Key = situation: (visited, shop)
    best = {}  # shortest distance from start for each situation, e.g. best[({0, 1}, P1)] = 1400
    prev = {}  # the situation before it, to rebuild the trip at the end

    # First stop: walk from start to any shop
    for kind, group in enumerate(candidates):
        for shop in group:
            situation = (frozenset([kind]), shop)
            best[situation] = dist(start, shop)
            prev[situation] = None

    # Add one stop at a time: first all situations with 1 kind visited, then 2, ...
    for size in range(1, len(candidates)):
        for (visited, shop), d in list(best.items()):
            if len(visited) != size:
                continue
            for kind, group in enumerate(candidates):
                if kind in visited:
                    continue  # this kind is already done
                for next in group:
                    new = (visited | {kind}, next)
                    new_d = d + dist(shop, next)
                    if new_d < best.get(new, float("inf")):
                        best[new] = new_d
                        prev[new] = (visited, shop)

    # Last step: every kind visited, walk to the end, take the shortest
    total, last = min((d + dist(shop, end), (visited, shop))
                      for (visited, shop), d in best.items() if visited == all_kinds)

    # Walk back through prev to get the stops in order
    stops = []
    while last is not None:
        stops.append(last[1])
        last = prev[last]
    return stops[::-1], total