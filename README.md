# Berlin Route Finder

Shortest walking and cycling routes on Berlin's real street network, computed on OpenStreetMap data and shown on an interactive map.

**Live:** https://berlin-route-finder.streamlit.app

The first version downloaded streets for every search and took over a minute per query. The current version loads the street graph once in about 5 seconds, then answers each search in under half a second.

![Screenshot](images/dashboard.png)

## How it got faster

| Version | What changed | Why |
|---|---|---|
| Live download | Fetched the streets around each search from the Overpass API | Easy to build, but every search took over a minute and broke when the server was busy |
| Caching | Cached geocoding results and graphs in memory | Searching the same route again is faster |
| Preloaded graphs | Built the walk and bike networks (5 km around Brandenburger Tor) once and loaded them at startup | Searches no longer wait for the internet at all |
| Compression | Stored the graphs as `.graphml.gz` | 89 MB → 9.7 MB (walk), 40 MB → 4.7 MB (bike), small enough to ship with the repo |

## Results

| Route | Distance | Live download | Preloaded | Speedup |
|---|---|---|---|---|
| Brandenburger Tor → Potsdamer Platz | 865 m | ~71 s | 0.18 s | ~390× |
| Hauptbahnhof → Alexanderplatz | 3.6 km | ~66 s | 0.26 s | ~250× |
| Zoologischer Garten → East Side Gallery | 8.5 km | ~114 s | 0.45 s | ~250× |

Walking routes, measured locally on a MacBook Air M3 (16 GB RAM), Python 3.14, OSMnx 2.1.

Preloaded: time per search after the walk graph (90,663 intersections) is loaded. Loading takes 5.5 s, once, when the app starts. Best of 5 runs (`benchmarks/benchmark.py`).

Live download: total time per search (download + routing), measured once per route (`benchmarks/benchmark_live.py`); timings depend on the load of the public Overpass server.

Both versions find the same routes. The download was almost all of the old cost: routing itself took under 0.4 s there too.

![Search time vs. route length](images/time_vs_length.png)

Over 200 random routes (best of 3 each), a search costs about 0.14 s plus 30 ms per km. The fixed part comes from finding the nearest intersections, which rebuilds a search index over all 90,000 intersections on every query. On the small graphs of the old version, the same short route took only 0.02 s. The growth flattens slightly for the longest routes, which cover most of the graph anyway.

## How it works

- **Graph:** OSMnx turns OpenStreetMap data into a directed graph. The walk network has 90,663 intersections, the bike network 37,980.
- **Geocoding:** place names are resolved with Nominatim and checked against the covered area.
- **Routing:** start and end snap to the nearest intersection, then NetworkX finds the shortest path weighted by street length.
- **App:** Streamlit, with the route kept in session state so it survives Streamlit's reruns.

## Limitations

- Only covers places within 5 km of Brandenburger Tor.
- Travel time uses average speeds (5 km/h walking, 15 km/h cycling).
- Snapping to the nearest intersection isn't always optimal: a slightly farther entry point can give a shorter total route.

## What's next

- Build the nearest-intersection index once instead of on every search, to remove most of the fixed 0.14 s.
- Smarter snapping that considers several nearby intersections, not just the closest one.
- A multi-stop tour that finds the best order to visit several places.

## Run locally

```bash
git clone https://github.com/ArvellLeoputra/berlin-route-finder.git
cd berlin-route-finder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To rebuild the street graphs: `python build_graph.py`.

To reproduce the timings: `python -m benchmarks.benchmark`, `python -m benchmarks.benchmark_live` and `python -m benchmarks.benchmark_scaling`.