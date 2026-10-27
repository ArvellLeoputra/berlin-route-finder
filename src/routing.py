import folium
import osmnx as ox
import networkx as nx
import numpy as np

from sklearn.neighbors import BallTree


def load_graph(start, end, mode="walk", buffer=500):
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    straight = ox.distance.great_circle(start[0], start[1], end[0], end[1])
    
    G = ox.graph_from_point(
        midpoint,
        dist=straight / 2 + buffer,
        network_type=mode
    )
    return G


def build_index(G):
    nodes = list(G.nodes)
    # lat/lon in radians, because haversine expects radians
    coords = np.radians([(G.nodes[n]["y"], G.nodes[n]["x"]) for n in nodes])
    # haversine = distance on a sphere
    tree = BallTree(coords, metric="haversine")
    return tree, nodes


def nearest_node(index, point):
    tree, nodes = index
    coords = np.radians([point])
    _, positions = tree.query(coords, k=1)
    return nodes[positions[0][0]]


def find_route(G, start, end, index=None):
    if index is None:
        start_node = ox.nearest_nodes(G, X=start[1], Y=start[0])
        end_node = ox.nearest_nodes(G, X=end[1], Y=end[0])
    else:
        start_node = nearest_node(index, start)
        end_node = nearest_node(index, end)

    distance, route = nx.bidirectional_dijkstra(G, start_node, end_node, weight="length")

    return route, distance


def make_map(G, route, distance, start_name, end_name):
    coords = []
    for node_id in route:
        node = G.nodes[node_id]
        coords.append((node["y"], node["x"]))

    m = folium.Map(tiles="Esri.WorldStreetMap")

    folium.PolyLine(
        locations=coords,
        color="blue",
        weight=5
    ).add_to(m)

    folium.Marker(
        location=coords[0],
        popup=start_name,
        icon=folium.Icon(color="green"),
        tooltip="Start",
    ).add_to(m)

    folium.Marker(
        location=coords[-1],
        popup=f"{end_name} – {distance:.0f} m",
        icon=folium.Icon(color="red"),
        tooltip="End",
    ).add_to(m)

    m.fit_bounds(coords)
    return m