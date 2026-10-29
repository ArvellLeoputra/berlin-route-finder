import osmnx as ox
import pytest

from src.routing import build_index


# Load each graph once and share it between all test files
@pytest.fixture(scope="session")
def walk():
    G = ox.load_graphml("data/walk.graphml.gz")
    return G, build_index(G)


@pytest.fixture(scope="session")
def bike():
    G = ox.load_graphml("data/bike.graphml.gz")
    return G, build_index(G)