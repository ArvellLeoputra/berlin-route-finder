import time
from routing import find_route


# fastest of n runs (s) and route length (m)
def best_time(G, start, end, index=None, repeats=5):
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        _, distance = find_route(G, start, end, index=index)
        best = min(best, time.perf_counter() - t0)
    return best, distance