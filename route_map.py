import folium
import osmnx as ox
import networkx as nx

G = ox.graph_from_address(
    "Straße des 17. Juni 135, Berlin, Germany",
    dist=1500,
    network_type="walk"
)

start_name, start = "TU Berlin", (52.5126, 13.3266)
end_name, end = "Zoologischer Garten", (52.5070, 13.3324)

start_node = ox.nearest_nodes(G, X=start[1], Y=start[0])
end_node = ox.nearest_nodes(G, X=end[1], Y=end[0])

route = nx.shortest_path(G, start_node, end_node, weight="length")
distance = nx.shortest_path_length(G, start_node, end_node, weight="length")

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
    tooltip="Start"
).add_to(m)

folium.Marker(
    location=coords[-1],
    popup=f"{end_name} – {distance:.0f} m, ~{distance / 83:.0f} min walk",
    icon=folium.Icon(color="red"),
    tooltip="End"
).add_to(m)

m.fit_bounds(coords)

m.save("route.html")