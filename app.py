import streamlit as st
import osmnx as ox
from streamlit_folium import st_folium
from routing import load_graph, find_route, make_map, build_index

CENTER = (52.5163, 13.3777)  # Brandenburger Tor coordinates
RADIUS = 5000


# Caching to avoid repeated geocoding
@st.cache_data(show_spinner=False)
def cached_geodata(place):
    return ox.geocode(f"{place}, Berlin, Germany")


def find_place(name, label):
    try:
        point = cached_geodata(name)
    except Exception:
        st.error(f"Couldn't find the {label} '{name}'. Try another name.")
        st.stop()

    dist = ox.distance.great_circle(CENTER[0], CENTER[1], point[0], point[1])
    if dist > RADIUS:
        st.error(f"The {label} '{name}' is outside the covered area (5 km around Brandenburger Tor).")
        st.stop()

    return point


# Caching to avoid repeated graph loading
@st.cache_resource(show_spinner=False)
def load_saved_graph(mode):
    return ox.load_graphml(f"data/{mode}.graphml.gz")


# Built once at launch, so searches only look things up
@st.cache_resource(show_spinner=False)
def load_index(mode):
    return build_index(load_saved_graph(mode))


st.title("Berlin Route Finder")
st.caption("Covers central Berlin, within 5 km of Brandenburger Tor.")

with st.spinner("Loading map data..."):
    for m in ("walk", "bike"):
        load_saved_graph(m)
        load_index(m)

start_name = st.text_input("Start")
end_name = st.text_input("Destination")

modes = {"Walk": ("walk", 5), "Bike": ("bike", 15)}
mode_label = st.radio("Mode", list(modes), horizontal=True)
mode, speed = modes[mode_label]

if st.button("Find route"):
    # start fresh, so a failed search doesn't bring back an old route
    for key in ["map", "distance", "speed", "query"]:
        st.session_state.pop(key, None)

    if not start_name or not end_name:
        st.warning("Please enter both a start and a destination.")
        st.stop()

    start = find_place(start_name, "start")
    end = find_place(end_name, "destination")

    with st.spinner("Loading streets..."):
        G = load_saved_graph(mode)
        index = load_index(mode)
    route, distance = find_route(G, start, end, index=index)

    # Keep the route between reruns, otherwise the map flashes and disappears
    st.session_state["map"] = make_map(G, route, distance, start_name, end_name)
    st.session_state["distance"] = distance
    st.session_state["speed"] = speed
    st.session_state["query"] = (start_name, end_name, mode_label)

if "map" in st.session_state:
    if st.session_state["query"] != (start_name, end_name, mode_label):
        st.info("You changed the inputs. Click **Find route** to update.")

    distance = st.session_state["distance"]
    distance_km = distance / 1000
    dist_text = f"{distance:.0f} m" if distance < 1000 else f"{distance_km:.1f} km"

    minutes = distance_km / st.session_state["speed"] * 60
    h, m = divmod(round(minutes), 60)
    time_text = f"~{h} h {m} min" if h > 0 else f"~{max(1, round(minutes))} min"

    col1, col2 = st.columns(2)
    col1.metric("Distance", dist_text)
    col2.metric("Time", time_text)

    s, e, m_label = st.session_state["query"]
    st.caption(f"{m_label} route from {s} to {e}")

    st_folium(st.session_state["map"], width=700, height=500, returned_objects=[])