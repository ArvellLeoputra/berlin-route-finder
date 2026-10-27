import random

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

from routing import build_index
from benchmarks.timing import best_time

G = ox.load_graphml("data/walk.graphml.gz")
nodes = list(G.nodes)
index = build_index(G)
random.seed(0)  # same random routes every run

old_t, new_t, dists = [], [], []
for i in range(200):
    a, b = random.sample(nodes, 2)
    start = (G.nodes[a]["y"], G.nodes[a]["x"])
    end = (G.nodes[b]["y"], G.nodes[b]["x"])

    try:
        t_old, d = best_time(G, start, end, repeats=3)
        t_new, _ = best_time(G, start, end, index=index, repeats=3)
    except nx.NetworkXNoPath:
        continue  # some pairs have no walkable connection
    old_t.append(t_old)
    new_t.append(t_new)
    dists.append(d / 1000)  # meters to km

    if (i + 1) % 20 == 0:
        print(f"{i + 1} of 200 routes done")

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.scatter(dists, old_t, alpha=0.5, s=15, label="without index")
ax.scatter(dists, new_t, alpha=0.5, s=15, label="with index")
ax.set_ylim(0, 0.5)
ax.set_xlabel("Route length (km)")
ax.set_ylabel("Search time (s)")
ax.set_title("Search time vs. route length (preloaded walk graph)")

leg = ax.legend(loc="upper left", frameon=False, markerscale=1.5)
for handle in leg.legend_handles:
    handle.set_alpha(1)
    
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("images/time_vs_length.png", dpi=150)

# points above the y-axis limit are not drawn, to avoid outliers
cut = sum(t > 0.5 for t in old_t + new_t)
if cut:
    print(f"{cut} point(s) above 0.5 s not shown")

mean_old = sum(old_t) / len(old_t)
mean_new = sum(new_t) / len(new_t)
print(f"{len(dists)} routes, mean {mean_old:.3f} s without index, {mean_new:.3f} s with index")