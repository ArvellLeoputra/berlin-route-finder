import folium
import osmnx as ox
import networkx as nx

def load_graph(start, end, mode="walk", buffer=500):
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    straight = ox.distance.great_circle(start[0], start[1], end[0], end[1])
    
    G = ox.graph_from_point(
        midpoint,
        dist=straight / 2 + buffer,
        network_type=mode
    )
    return G


def find_route(G, start, end):
    start_node = ox.nearest_nodes(G, X=start[1], Y=start[0])
    end_node = ox.nearest_nodes(G, X=end[1], Y=end[0])

    route = nx.shortest_path(G, start_node, end_node, weight="length")
    distance = nx.shortest_path_length(G, start_node, end_node, weight="length")

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