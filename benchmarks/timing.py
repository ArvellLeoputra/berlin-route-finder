import time

from src.routing import find_route


# fastest of n runs (s) and route length (m)
def best_time(G, start, end, index=None, repeats=5, algorithm="bidirectional"):
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        _, distance = find_route(G, start, end, index=index, algorithm=algorithm)
        best = min(best, time.perf_counter() - t0)
    return best, distance


# Run one planner once, return its result and how long it took (s)
def timed_plan(planner, *args, **kwargs):
    t0 = time.perf_counter()
    stops, distance, _ = planner(*args, **kwargs)
    return stops, distance, time.perf_counter() - t0
