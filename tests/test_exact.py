import networkx as nx
import pytest

from src.exact import plan_trip_exact
from src.planner import plan_trip
from tests.test_planner import HOME, KINDS, SKETCH_SHOPS, UNI


# Test 1: the exact planner finds the best trip from the README figure
def test_exact_finds_best_trip_from_figure(walk):
    G, index = walk
    stops, distance, _ = plan_trip_exact(G, index, UNI, HOME, SKETCH_SHOPS, KINDS)
    assert round(distance) == 8684
    assert [s.kind for s in stops] == ["Post office", "Pharmacy", "Groceries"]


# Test 2: one shop of each kind, and the route really has the reported length
def test_exact_trip_is_consistent(walk):
    G, index = walk
    stops, distance, route = plan_trip_exact(G, index, UNI, HOME, SKETCH_SHOPS, KINDS)
    assert sorted(s.kind for s in stops) == sorted(KINDS)
    assert nx.path_weight(G, route, weight="length") == pytest.approx(distance)


# Test 3: the exact planner is never worse than the shortlist planner
@pytest.mark.parametrize("k", [1, 2])
def test_exact_never_worse_than_shortlist(walk, k):
    G, index = walk
    _, exact, _ = plan_trip_exact(G, index, UNI, HOME, SKETCH_SHOPS, KINDS)
    _, shortlist, _ = plan_trip(G, index, UNI, HOME, SKETCH_SHOPS, KINDS, k=k)
    assert exact <= shortlist + 1e-6