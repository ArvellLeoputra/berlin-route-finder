import os
import osmnx as ox

CENTER = (52.5163, 13.3777)  # Brandenburger Tor coordinates
RADIUS = 5000

os.makedirs("data", exist_ok=True)

for mode in ["walk", "bike"]:
    print(f"Downloading {mode} network...")
    G = ox.graph_from_point(CENTER, dist=RADIUS, network_type=mode)
    filename = f"data/{mode}.graphml.gz"
    ox.save_graphml(G, filename)
    print(f"Saved {filename} ({len(G.nodes)} nodes)")