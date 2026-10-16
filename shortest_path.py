import osmnx as ox
import networkx as nx

G = ox.graph_from_address(
    "Straße des 17. Juni 135, Berlin, Germany",
    dist=1500,
    network_type="walk"
)

start = (52.5126, 13.3266)  # TU Berlin
end = (52.5070, 13.3324)    # Zoologischer Garten

start_node = ox.nearest_nodes(G, X=start[1], Y=start[0])  # nearest node to start
end_node = ox.nearest_nodes(G, X=end[1], Y=end[0])      # nearest node to end

route = nx.shortest_path(G, start_node, end_node, weight="length")
distance = nx.shortest_path_length(G, start_node, end_node, weight="length")

print(f"Distance: {distance:.0f} m")
print(f"Intersections on route: {len(route)}")
ox.plot_graph_route(G, route, node_size=0)