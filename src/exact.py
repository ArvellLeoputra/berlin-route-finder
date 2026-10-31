import heapq
import itertools

import networkx as nx

from src.routing import make_heuristic, nearest_node


def plan_trip_exact(G, index, start, end, shops, kinds):
    """
    Best trip from start to end visiting one shop of each kind, using all shops.

    Imagine one copy of the street map for each set of errands done. Walking along a street
    stays in the same copy. At a shop of a missing kind, you move to the copy where that kind
    is done, for free. One A* search from (start, nothing done) to (end, everything done)
    then finds the guaranteed best trip.

    Returns (stops in visiting order, total distance in m, route as a list of graph nodes).
    """
    # Which errands can be done at each intersection
    shops_at = {}  # intersection -> errands available
    for kind in kinds:
        for shop in shops[kind]:
            node = nearest_node(index, (shop.lat, shop.lon))
            here = shops_at.setdefault(node, {})  # the shops at this intersection
            if kind not in here:
                here[kind] = shop  # one shop per kind is enough

    source = nearest_node(index, start)
    target = nearest_node(index, end)
    all_done = frozenset(kinds)
    guide = make_heuristic(G, target)  # straight-line distance to the end

    # A state is (intersection, errands done)
    first = (source, frozenset())
    best = {first: 0.0}   # state -> shortest distance from the start
    prev = {first: None}  # state -> (state before it, shop visited on the way or None)
    order = itertools.count()  # tie-breaker for same heap[0] (walk + straight line distance)
    heap = [(guide(source), next(order), first)]

    def relax(old, new, d, shop):
        # Keep the new state if this is the shortest way to it so far
        if d < best.get(new, float("inf")):
            best[new] = d
            prev[new] = (old, shop)  # remember where we came from, to rebuild the trip later
            heapq.heappush(heap, (d + guide(new[0]), next(order), new))

    while heap:
        _, _, state = heapq.heappop(heap)  # take the state with the smallest walk so far + straight line to the end
        node, done = state

        if node == target and done == all_done:  # at the end with all errands done
            return rebuild(prev, state, best[state])  # rebuild the path

        # Do an errand here, if a shop of a missing kind is at this intersection
        for kind, shop in shops_at.get(node, {}).items():
            if kind not in done:
                 relax(state, (node, done | {kind}), best[state], shop)  # same place, errand ticked off, 0 m extra

        # Walk along a street to a neighbouring intersection
        for nxt, edges in G[node].items():
            length = min(e["length"] for e in edges.values())  # two intersections can have several streets, take the shortest
            relax(state, (nxt, done), best[state] + length, None)

    raise nx.NetworkXNoPath("No trip found")


def rebuild(prev, state, distance):
    # Walk back from the final state to collect the route and the shops in order
    route, stops = [], []
    while state is not None:
        node = state[0]
        if not route or route[-1] != node:  # skip repeats: doing an errand stays at the same intersection
            route.append(node)
        step = prev[state]
        if step is None:  # reached the start, nothing before it
            break
        state, shop = step
        if shop is not None:
            stops.append(shop)
    return stops[::-1], distance, route[::-1]