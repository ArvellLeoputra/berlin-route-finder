import osmnx as ox
import requests
import streamlit as st
from osmnx._errors import InsufficientResponseError
from streamlit_folium import st_folium

from src.compact_graph import load_compact
from src.config import CENTER, RADIUS
from src.exact import plan_trip_exact
from src.planner import load_shops
from src.routing import STOP_COLORS, build_index, find_route, make_map

st.set_page_config(page_title="Berlin Route Finder", page_icon="🗺️", layout="wide")

# Caching to avoid repeated geocoding
@st.cache_data(show_spinner=False)
def cached_geodata(place):
    return ox.geocode(f"{place}, Berlin, Germany")


def find_place(name, label):
    try:
        point = cached_geodata(name)
    except (InsufficientResponseError, ValueError):
        st.error(f"Couldn't find the {label} '{name}'. Try another name.")
    except requests.RequestException:
        st.error("Couldn't reach the map service. Check your connection and try again.")
    st.stop()

    dist = ox.distance.great_circle(CENTER[0], CENTER[1], point[0], point[1])
    if dist > RADIUS:
        st.error(f"The {label} '{name}' is outside the covered area (5 km around Brandenburger Tor).")
        st.stop()

    return point


# Caching to avoid repeated graph loading
@st.cache_resource(show_spinner=False)
def load_saved_graph(mode):
    return load_compact(mode)


# Built once at launch, so searches only look things up
@st.cache_resource(show_spinner=False)
def load_index(mode):
    return build_index(load_saved_graph(mode))


# Shops for the errand planner, read once
@st.cache_resource(show_spinner=False)
def load_saved_shops():
    return load_shops()


def format_distance(meters):
    return f"{meters:.0f} m" if meters < 1000 else f"{meters / 1000:.2f} km"


def format_time(meters, speed):
    minutes = round(meters / 1000 / speed * 60)
    h, m = divmod(minutes, 60)
    return f"{h} h {m} min" if h > 0 else f"{max(1, minutes)} min"


def stop_row(color, label, name, number=""):
    # One line of the stops list: a coloured dot (with the stop number) and the place
    return (
        f'<div style="display:flex;align-items:center;gap:12px;margin:0 0 14px 0">'
        f'<div style="background:{color};color:white;border-radius:50%;width:28px;height:28px;'
        f'flex:none;display:flex;align-items:center;justify-content:center;'
        f'font-weight:700;font-size:13px">{number}</div>'
        f'<div><div style="color:#6b7280;font-size:12px">{label}</div>'
        f'<div style="font-weight:600">{name}</div></div></div>'
    )


# Warm up the cache at launch, so the first search doesn't have to wait
with st.spinner("Loading map data..."):
    graphs = {mode_name: load_saved_graph(mode_name) for mode_name in ("walk", "bike")}
    indexes = {mode_name: load_index(mode_name) for mode_name in ("walk", "bike")}

# Sidebar: all inputs
modes = {"Walk": ("walk", 5), "Bike": ("bike", 15)}

with st.sidebar:
    st.title("Berlin Route Finder")
    st.caption("Errands on the way home, central Berlin")

    start_name = st.text_input("Start")
    end_name = st.text_input("Destination")
    mode_label = st.segmented_control("Mode", list(modes), default="Walk", required=True, width="stretch")
    errands = st.multiselect("Errands on the way (optional)", sorted(load_saved_shops()))
    clicked = st.button("Find route", type="primary", width="stretch")

    st.caption("Covers 5 km around Brandenburger Tor. "
               "Street and shop data © OpenStreetMap contributors.")

mode, speed = modes[mode_label]

if clicked:
    # start fresh, so a failed search doesn't bring back an old route
    for key in ["map", "distance", "direct", "speed", "query", "stops"]:
        st.session_state.pop(key, None)

    if not start_name or not end_name:
        st.warning("Please enter both a start and a destination.")
        st.stop()

    start = find_place(start_name, "start")
    end = find_place(end_name, "destination")

    # Use the graph and index already loaded at launch
    G = graphs[mode]
    index = indexes[mode]

    direct_route, direct = find_route(G, start, end, index=index, algorithm="astar")
    if errands:
        with st.spinner("Planning your errands..."):
            stops, distance, route = plan_trip_exact(G, index, start, end, load_saved_shops(), errands)
    else:
        stops = []
        distance, route = direct, direct_route

    # Keep the result between reruns, otherwise the map flashes and disappears
    st.session_state["map"] = make_map(G, route, distance, start_name, end_name, stops=stops)
    st.session_state["distance"] = distance
    st.session_state["direct"] = direct
    st.session_state["speed"] = speed
    st.session_state["stops"] = stops
    st.session_state["query"] = (start_name, end_name, mode_label, tuple(errands))

# Main area: the result
if "map" not in st.session_state:
    st.header("Plan your walk home")
    st.write("Enter a start and a destination on the left, add the errands you need, "
             "and the app picks which shops to visit and in what order.")
    st.stop()

if st.session_state["query"] != (start_name, end_name, mode_label, tuple(errands)):
    st.info("You changed the inputs. Click **Find route** to update.")

start, end, m_label, done = st.session_state["query"]
distance, stops = st.session_state["distance"], st.session_state["stops"]

st.header("Your trip")
errand_text = f", {len(done)} errand{'s' if len(done) != 1 else ''}" if done else ""
st.caption(f"{start} → {end}, {m_label.lower()}{errand_text}")

# Result
col1, col2, col3, col4 = st.columns(4)
col1.metric("Distance", format_distance(distance), border=True)
col2.metric("Time", format_time(distance, st.session_state["speed"]), border=True)
col3.metric("Errands add", f"+{format_distance(distance - st.session_state['direct'])}", border=True)
col4.metric("Stops", len(stops), border=True)

# Map and stops list side by side
map_col, list_col = st.columns([3, 1])
with map_col:
    st_folium(st.session_state["map"], height=560, use_container_width=True, returned_objects=[])
with list_col:
    st.subheader("Stops")
    rows = [stop_row("white;border:3px solid #151a24;box-sizing:border-box", "Start", start)]
    rows += [stop_row(STOP_COLORS.get(stop.kind, "gray"), stop.kind, stop.name or "Unnamed", number)
             for number, stop in enumerate(stops, start=1)]
    rows.append(stop_row("#151a24", "End", end))
    st.markdown("".join(rows), unsafe_allow_html=True)
