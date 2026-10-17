import streamlit as st
import osmnx as ox
from streamlit_folium import st_folium
from routing import load_graph, find_route, make_map


# Caching to avoid repeated geocoding
@st.cache_data(show_spinner=False)
def cached_geodata(place):
    return ox.geocode(f"{place}, Berlin, Germany")


def find_place(name, label):
    try:
        return cached_geodata(name)
    except Exception:
        st.error(f"Couldn't find the {label} '{name}'. Try another name.")
        st.stop()


# Caching to avoid repeated graph loading
@st.cache_resource(show_spinner=False)
def cached_graph(start, end, mode):
    return load_graph(start, end, mode=mode)


st.title("Berlin Route Finder")

start_name = st.text_input("Start")
end_name = st.text_input("Destination")

modes = {"Walk": ("walk", 5), "Bike": ("bike", 15)}
mode_label = st.radio("Mode", list(modes), horizontal=True)
mode, speed = modes[mode_label]

if st.button("Find route"):
    if not start_name or not end_name:
        st.warning("Please enter both a start and a destination.")
        st.stop()

    start = find_place(start_name, "start")
    end = find_place(end_name, "destination")

    with st.spinner("Loading streets..."):
        G = cached_graph(start, end, mode)
    route, distance = find_route(G, start, end)

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