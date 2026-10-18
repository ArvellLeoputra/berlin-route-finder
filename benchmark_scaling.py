import random, time
import osmnx as ox
import matplotlib.pyplot as plt
import numpy as np

from routing import find_route

G = ox.load_graphml("data/walk.graphml.gz")
nodes = list(G.nodes)
random.seed(0)  # same random routes every run

dists, times = [], []
for _ in range(200):
    a, b = random.sample(nodes, 2)
    start = (G.nodes[a]["y"], G.nodes[a]["x"])
    end = (G.nodes[b]["y"], G.nodes[b]["x"])

    # time each route 3 times and keep the fastest, to reduce noise
    best = float("inf")
    try:
        for _ in range(3):
            t0 = time.perf_counter()
            _, d = find_route(G, start, end)
            best = min(best, time.perf_counter() - t0)
    except Exception:
        continue  # some pairs have no walkable connection
    times.append(best)
    dists.append(d / 1000)

# straight-line fit: intercept = fixed cost, slope = extra time per km
slope, intercept = np.polyfit(dists, times, 1)
xs = np.linspace(0, max(dists), 100)

plt.scatter(dists, times, alpha=0.5, s=15)
plt.plot(xs, slope * xs + intercept, color="red",
         label=f"fit: {intercept:.2f} s + {slope * 1000:.0f} ms/km")
plt.ylim(bottom=0)
plt.xlabel("Route length (km)")
plt.ylabel("Search time (s)")
plt.title("Search time vs. route length (preloaded walk graph)")
plt.legend()
plt.tight_layout()
plt.savefig("time_vs_length.png", dpi=150)

print(f"{len(times)} routes, fixed cost {intercept:.3f} s, {slope * 1000:.1f} ms per km")