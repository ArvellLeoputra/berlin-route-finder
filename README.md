# Berlin Route Finder

![Tests](https://github.com/ArvellLeoputra/berlin-route-finder/actions/workflows/tests.yml/badge.svg)

On my way home from uni, I usually have a few things to do: drop off a parcel, grab something from the pharmacy, buy groceries. Google Maps can do it, but I have to pick which post office, which pharmacy and which supermarket myself, one by one. So I built an app that just figures it out: tell it where I start, where I'm going, and what I need, and it finds the shortest way through everything.

![Idea sketch of the errand planner](images/idea-sketch.png)

## Why not just go to the nearest one?

Picking the nearest shop each time feels like the obvious move. But the nearest one now isn’t always the best one for the whole trip home.

![Nearest next shop vs best combination](images/nearest-vs-best.png)

Same shops, same start and end: 10.4 km if I always take the nearest one, 8.7 km for the best combination.

How many trips are there? Pick one of 3 post offices, 3 pharmacies and 3 supermarkets, then visit them in any of 6 orders: 162 trips. Fine for a computer. With 5 errands and 5 branches each, it's already 375,000, and that's where it becomes a real optimization problem. In research, this is known as the [Trip Planning Query](https://doi.org/10.1007/11535331_16).

## What it does

**Live:** https://berlin-route-finder.streamlit.app

Enter a start and a destination, pick walking or cycling, and optionally add errands: post office, pharmacy, groceries, bakery, ATM, drugstore. The app picks one real shop of each kind and the order to visit them, and shows the trip on the map with numbered stops.

![Screenshot](images/dashboard.png)

It's built in two layers:

1. **Fast routing** between two points on Berlin's real street network. My first version took over a minute per search. Now it takes milliseconds.

2. **The errand planner** on top, which uses that routing to compare many possible trips.

## How the planner works

Berlin has a lot of shops: in the covered area there are 63 post offices, 201 pharmacies, 398 supermarkets, 493 bakeries, 572 ATMs and 93 drugstores. Trying every combination is impossible (for 3 errands alone, about 30 million trips), so the planner works in two steps.

1. **Shortlist.** For each kind, keep the 5 shops with the smallest detour in straight lines (start → shop → end). This only needs arithmetic, no routing. Then compute real walking routes only between the start, the end and the shortlisted shops, each pair once.

2. **Dynamic programming.** Instead of building every full trip, build trips one stop at a time and keep only the shortest way to each state: which kinds are visited, and which shop I'm standing at. For example, `Uni → P1 → Ph1` and `Uni → P2 → Ph1` both end at the pharmacy with the post office done. Whatever comes next is the same for both, so only the shorter one is kept and continued. This is the Held–Karp idea from the travelling salesman problem.

With 6 errands and 5 shops each, that's about 2,000 states instead of 11 million trips, and the search itself runs in milliseconds. Almost all of the planning time goes into the walking routes between the shortlisted places.

The shortlist is a heuristic: a shop that looks like a detour in a straight line can still have a direct street, so a small shortlist can miss the best trip. A bigger shortlist is safer but slower:

| Shortlist per kind | Possible trips | Best trip found | Time |
|---|---|---|---|
| 3 | 162 | 6.85 km | 0.42 s |
| 5 | 750 | 6.67 km | 1.24 s |
| 8 | 3,072 | 6.67 km | 2.92 s |
| 10 | 6,000 | 6.64 km | 5.45 s |

TU Berlin → Alexanderplatz with a post office, a pharmacy and groceries, walking, on a MacBook Pro (M1 Pro), `benchmarks/benchmark_planner.py`. Going straight home is about 6.2 km, so with the right shops the three errands only add about 400 m. The app uses 5 shops per kind.

## How the routing got faster

| Version | What changed | Why |
|---|---|---|
| Live download | Fetched the streets around each search from the Overpass API | Easy to build, but every search took over a minute and broke when the server was busy |
| Caching | Cached geocoding results and graphs in memory | Searching the same route again is faster |
| Preloaded graphs | Built the walk and bike networks (5 km around Brandenburger Tor) once and loaded them at startup | Searches no longer download street data |
| Compression | Stored the graphs as `.graphml.gz` | 89 MB → 9.7 MB (walk), 40 MB → 4.7 MB (bike), small enough to ship with the repo |
| Prebuilt index | Built the nearest-intersection lookup once at startup instead of on every search | OSMnx prepared its lookup from scratch on each call, a fixed cost of about 0.2 s per search |
| Single search | Took the route and its length from one bidirectional search instead of two | The length came from a second, one-directional Dijkstra search; now both come from the search that finds the route |
| A* search | Replaced the bidirectional search with A*, which uses the straight-line distance to the destination as a guide | Checks fewer intersections, and since the guide never overestimates, the routes stay the same (2.4–3.5× faster) |

## Routing results

| Route | Distance | Live download (first version) | Now | Speedup |
|---|---|---|---|---|
| Brandenburger Tor → Potsdamer Platz | 865 m | ~71 s | 0.002 s | >10,000× |
| Hauptbahnhof → Alexanderplatz | 3.6 km | ~66 s | 0.030 s | ~2,200× |
| Zoologischer Garten → East Side Gallery | 8.5 km | ~114 s | 0.144 s | ~800× |

Walking routes, measured locally on a MacBook Pro (M1 Pro, 16 GB RAM), Python 3.13, OSMnx 2.1.1. Timings cover the nearest-intersection lookup and the path search, not the geocoding of place names.

Now: time per search with the bidirectional search, after startup, best of 5 runs (`benchmarks/benchmark.py`). Startup happens once: the walk graph (90,663 intersections) loads in 5.8 s and its index builds in 0.07 s. The bike graph (37,980 intersections) loads in 3.0 s and its index builds in 0.03 s.

Live download: total time per search (download + routing), measured once per route on a MacBook Air M3 (`benchmarks/benchmark_live.py`). These times depend mainly on the load of the public Overpass server, not on the laptop.

All versions find the same routes. The download was almost all of the original cost: routing itself took under 0.4 s there too.

### A* vs bidirectional search

| Route | Distance | Bidirectional | A* | Speedup |
|---|---|---|---|---|
| Brandenburger Tor → Potsdamer Platz | 865 m | 0.002 s | 0.001 s | 2.7× |
| Hauptbahnhof → Alexanderplatz | 3.6 km | 0.031 s | 0.009 s | 3.5× |
| Zoologischer Garten → East Side Gallery | 8.5 km | 0.148 s | 0.062 s | 2.4× |

A* uses the straight-line distance to the destination as a guide, so it checks fewer intersections. The guide is never longer than the real distance, so A* finds the same shortest routes; the tests check this. Same machine and method as above, best of 5 runs (`benchmarks/benchmark_astar.py`), speedups from unrounded times. The live app uses A*. The chart below was measured with the bidirectional search.

![Search time vs. route length](images/time_vs_length.png)

The same 200 random routes, each timed best of 3, with and without the index (`benchmarks/benchmark_scaling.py`). Without it, every search pays a fixed cost of about 0.2 s, because OSMnx prepares its lookup over all 90,663 intersections from scratch on each call. Building it once removes that cost, so short routes now take a few milliseconds. What remains is the path search itself, which grows with route length, up to about 0.17 s for 12 km. Across the 200 routes, the mean search time is 0.28 s without the index and 0.07 s with it.

## Tests

Run `pytest` to run 14 tests:
- **Routing:** known walking and biking distances, the fast nearest-intersection index gives the same result as OSMnx, and A* finds the same distances as the bidirectional search.
- **Planner:** the shop data loads, the planner finds the 8.7 km trip from the figure above, every trip visits each kind once and its route really has the reported length, and the dynamic programming search gives the same result as trying every trip.


## How it works

- **Graph:** OSMnx turns OpenStreetMap data into a directed graph. The walk network has 90,663 intersections, the bike network 37,980.
- **Shops:** downloaded once from OpenStreetMap and saved in `data/shops.csv` (1,820 shops), so the app needs no internet for them.
- **Geocoding:** place names are resolved with Nominatim and checked against the covered area.
- **Routing:** start and end snap to the nearest intersection using a BallTree built once at startup, then an A* search in NetworkX, guided by the straight-line distance to the destination, finds the shortest path, weighted by street length.
- **Planner:** shortlist per kind, walking routes between the shortlisted places (each pair computed once), then dynamic programming over "kinds visited + current shop".
- **App:** Streamlit, with the graphs, indexes and shops loaded at startup and the route kept in session state so it survives Streamlit's reruns.

## Project structure

```
app.py                 Streamlit app (entry point)
src/
  routing.py           graph helpers, nearest-intersection index, routing, map
  planner.py           errand planner: shortlist and dynamic programming
  config.py            covered area (center and radius)
  build_graph.py       downloads and saves the street graphs
  build_shops.py       downloads and saves the shops
benchmarks/            timing scripts
tests/                 pytest tests
data/                  street graphs (.graphml.gz) and shops (shops.csv)
images/                screenshots, figures and benchmark chart
```

## Limitations

- Only covers places within 5 km of Brandenburger Tor.
- Travel time uses average speeds (5 km/h walking, 15 km/h cycling).
- The shortlist can miss the best shop, so the planner finds a very good trip, not always the best one.
- Shops come from OpenStreetMap: some have no name, opening hours are ignored, and "post office" includes the small Deutsche Post / DHL partner shops in kiosks.
- Snapping to the nearest intersection isn't always optimal: a slightly farther entry point can give a shorter total route.
- The live app runs on a free server, so its startup is likely slower than the laptop numbers above, and it goes to sleep when nobody uses it for a while.

## What's next

- An exact planner that searches the whole street map without a shortlist, so it always finds the best trip. Then I can measure how often the shortlist misses it, and by how much.
- Order rules, like "groceries last", so I don't carry shopping bags around.
- Opening hours, to skip shops that are closed.

## Run locally

```bash
git clone https://github.com/ArvellLeoputra/berlin-route-finder.git
cd berlin-route-finder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To download the data again (needs internet): 
- `python -m src.build_graph` for the street graphs
- `python -m src.build_shops` for the shops.

To reproduce the timings:

- `python -m benchmarks.benchmark`: startup and search times
- `python -m benchmarks.benchmark_live`: the first version (needs internet)
- `python -m benchmarks.benchmark_scaling`: the 200-route chart
- `python -m benchmarks.benchmark_astar`: A* vs bidirectional search
- `python -m benchmarks.benchmark_planner`: planner with different shortlist sizes

To run the tests: `pytest`

## Data

Street and shop data © OpenStreetMap contributors, available under the Open Database License.