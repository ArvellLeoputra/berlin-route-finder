import osmnx as ox
import pytest

from src.routing import find_route, nearest_node


# Test 1: the three benchmark routes give their known walking distances (in meters)
@pytest.mark.parametrize("start, end, expected", [
    ((52.5163, 13.3777), (52.5096, 13.3760), 865),  # Brandenburger Tor -> Potsdamer Platz
    ((52.5251, 13.3694), (52.5219, 13.4132), 3570), # Berlin Hauptbahnhof -> Alexanderplatz
    ((52.5070, 13.3324), (52.5050, 13.4397), 8460)  # Zoologischer Garten -> East Side Gallery
])
def test_known_walking_distances(walk, start, end, expected):
    G, index = walk
    _, distance = find_route(G, start, end, index=index)
    assert round(distance) == expected


# Test 2: our fast nearest-intersection index picks the same intersection as OSMnx
def test_index_matches_osmnx(walk):
    G, index = walk
    points = [
        (52.5163, 13.3777),
        (52.5070, 13.3324),
        (52.5219, 13.4132)
    ]

    for lat, lon in points:
        node_index = nearest_node(index, (lat, lon))
        node_osmnx = ox.distance.nearest_nodes(G, X=lon, Y=lat)
        assert node_index == node_osmnx


# Test 3: the bike graph gives the known distance for Brandenburger Tor -> Alexanderplatz
def test_known_bike_distance(bike):
    G, index = bike
    start = (52.5163, 13.3777)
    end = (52.5219, 13.4132)

    _, distance = find_route(G, start, end, index=index)
    assert round(distance) == 2727


# Test 4: A* finds the same distance as the bidirectional search (3 routes)
@pytest.mark.parametrize("start, end", [
    ((52.5163, 13.3777), (52.5096, 13.3760)),
    ((52.5251, 13.3694), (52.5219, 13.4132)),
    ((52.5070, 13.3324), (52.5050, 13.4397)),
])
def test_astar_matches_bidirectional(walk, start, end):
    G, index = walk
    _, dist_bidirectional = find_route(G, start, end, index=index)
    _, dist_astar = find_route(G, start, end, index=index, algorithm="astar")
    assert dist_astar == pytest.approx(dist_bidirectional)


# Test 5: an unknown algorithm name gives a clear error instead of a wrong result
def test_unknown_algorithm(walk):
    G, index = walk
    start = (52.5163, 13.3777)
    end = (52.5096, 13.3760)

    with pytest.raises(ValueError):
        find_route(G, start, end, index=index, algorithm="other_algorithm")