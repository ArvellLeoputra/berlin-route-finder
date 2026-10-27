import os
import osmnx as ox

from src.config import CENTER, RADIUS


def main():
    os.makedirs("data", exist_ok=True)

    for mode in ["walk", "bike"]:
        print(f"Downloading {mode} network...")
        G = ox.graph_from_point(CENTER, dist=RADIUS, network_type=mode)
        filename = f"data/{mode}.graphml.gz"
        ox.save_graphml(G, filename)
        print(f"Saved {filename} ({len(G.nodes)} nodes)")

if __name__ == "__main__":
    main()