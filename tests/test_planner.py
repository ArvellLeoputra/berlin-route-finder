import networkx as nx
import pytest
import itertools
import random

from src.planner import Shop, load_shops, plan_trip, best_trip
from src.routing import find_route

UNI = (52.5125, 13.3269)    # TU Berlin
HOME = (52.5219, 13.4132)   # Alexanderplatz
KINDS = ["Post office", "Pharmacy", "Groceries"]

# The made-up shops from the README figures (3 of each kind)
SKETCH_SHOPS = {
    "Post office": [Shop("Post office", "", 52.5100, 13.3500),
                    Shop("Post office", "", 52.5290, 13.3600),
                    Shop("Post office", "", 52.5020, 13.3950)],
    "Pharmacy":    [Shop("Pharmacy", "", 52.5165, 13.3880),
                    Shop("Pharmacy", "", 52.5050, 13.3350),
                    Shop("Pharmacy", "", 52.5310, 13.3720)],
    "Groceries":   [Shop("Groceries", "", 52.5300, 13.4010),
                    Shop("Groceries", "", 52.5010, 13.3700),
                    Shop("Groceries", "", 52.5050, 13.4060)],
}


# Test 1: the saved shop file has all three kinds
def test_load_shops():
    shops = load_shops()
    for kind in KINDS:
        assert len(shops[kind]) > 0


# Test 2: with every shop on the shortlist, the planner finds the best trip from the README figure
def test_finds_best_trip_from_figure(walk):
    G, index = walk
    stops, distance, _ = plan_trip(G, index, UNI, HOME, SKETCH_SHOPS, KINDS, k=3)
    assert round(distance) == 8684
    assert [s.kind for s in stops] == ["Post office", "Pharmacy", "Groceries"]


# Test 3: the trip visits exactly one shop of each kind, and the route really has that length
def test_trip_is_consistent(walk):
    G, index = walk
    stops, distance, route = plan_trip(G, index, UNI, HOME, SKETCH_SHOPS, KINDS, k=2)
    assert sorted(s.kind for s in stops) == sorted(KINDS)
    assert nx.path_weight(G, route, weight="length") == pytest.approx(distance)


# Test 4: with no errands, the trip is just the direct route
def test_no_errands(walk):
    G, index = walk
    stops, distance, _ = plan_trip(G, index, UNI, HOME, SKETCH_SHOPS, [])
    _, direct = find_route(G, UNI, HOME, index=index, algorithm="astar")
    assert stops == []
    assert distance == pytest.approx(direct)


# Test 5: dynamic programming finds the same best trip as trying every trip
def test_best_trip_matches_brute_force():
    random.seed(1)
    for _ in range(100):
        n, k = random.randint(0, 4), random.randint(1, 3)
        groups = [[f"{i}-{s}" for s in range(k)] for i in range(n)]
        table = {}

        def dist(a, b):
            if (a, b) not in table:
                table[a, b] = random.uniform(100, 3000)
            return table[a, b]

        brute = min(sum(dist(a, b) for a, b in zip(trip, trip[1:]))
                    for choice in itertools.product(*groups)
                    for order in itertools.permutations(choice)
                    for trip in [["start", *order, "end"]])
        _, d = best_trip("start", "end", groups, dist)
        assert d == pytest.approx(brute)