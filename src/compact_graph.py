import gzip
import pickle

import networkx as nx
import osmnx as ox


def compact(G):
    # Keep only what routing needs: intersection coordinates and street lengths
    S = nx.MultiDiGraph()
    S.graph.update(G.graph)  # keeps the coordinate system info that OSMnx needs
    S.add_nodes_from((n, {"x": d["x"], "y": d["y"]}) for n, d in G.nodes(data=True))
    S.add_edges_from((u, v, k, {"length": d["length"]}) for u, v, k, d in G.edges(keys=True, data=True))
    return S


def load_compact(mode):
    # Much faster to load and uses about a third of the memory of the .graphml file
    with gzip.open(f"data/{mode}_compact.pkl.gz", "rb") as f:
        return pickle.load(f)


def main():
    # Turn the saved .graphml.gz graphs into compact versions for the app
    for mode in ["walk", "bike"]:
        G = compact(ox.load_graphml(f"data/{mode}.graphml.gz"))
        filename = f"data/{mode}_compact.pkl.gz"
        with gzip.open(filename, "wb") as f:
            pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Saved {filename} ({len(G.nodes)} nodes)")


if __name__ == "__main__":
    main()