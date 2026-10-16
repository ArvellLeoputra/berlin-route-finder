import osmnx as ox

# area around TU Berlin (1.5 km radius)
G = ox.graph_from_address(
    "Straße des 17. Juni 135, Berlin, Germany",
    dist=1500,
    network_type="walk"
)

print("Nodes (intersections):", len(G.nodes))
print("Edges (street segments):", len(G.edges))

first_node = list(G.nodes(data=True))[0]
print("\nExample node:", first_node)

first_edge = list(G.edges(data=True))[0]
print("\nExample edge:", first_edge)

ox.plot_graph(G, node_size=0, edge_linewidth=0.5)