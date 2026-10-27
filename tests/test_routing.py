import osmnx as ox
import pytest

from routing import build_index, find_route, nearest_node

# Load each graph once and share it between all tests
@pytest.fixture(scope="module")
def walk():
    G = ox.load_graphml("data/walk.graphml.gz")
    return G, build_index(G)


@pytest.fixture(scope="module")
def bike():
    G = ox.load_graphml("data/bike.graphml.gz")
    return G, build_index(G)


# The benchmark routes, with their known walking distances in meters
@pytest.mark.parametrize("start, end, expected", [
    ((52.5163, 13.3777), (52.5096, 13.3760), 865),  # Brandenburger Tor -> Potsdamer Platz
    ((52.5251, 13.3694), (52.5219, 13.4132), 3570), # Berlin Hauptbahnhof -> Alexanderplatz
    ((52.5070, 13.3324), (52.5050, 13.4397), 8460)  # Zoologischer Garten -> East Side Gallery
])
def test_known_walking_distances(walk, start, end, expected):
    G, index = walk
    _, distance = find_route(G, start, end, index=index)
    assert round(distance) == expected


def test_index_matches_osmnx(walk):
    G, index = walk
    points = [(52.5163, 13.3777), (52.5070, 13.3324), (52.5219, 13.4132)]

    # Check that the nearest node found by our index matches OSMnx's nearest node
    for lat, lon in points:
        node_index = nearest_node(index, (lat, lon))
        node_osmnx = ox.distance.nearest_nodes(G, X=lon, Y=lat)
        assert node_index == node_osmnx


def test_bike_route_exists(bike):
    G, index = bike
    start = (52.5163, 13.3777)
    end = (52.5219, 13.4132)

    route, distance = find_route(G, start, end, index=index)
    assert distance > 0
    assert len(route) > 1