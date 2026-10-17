import streamlit as st
import osmnx as ox
from streamlit_folium import st_folium
from routing import load_graph, find_route, make_map


# Caching to avoid repeated geocoding
@st.cache_data
def cached_geodata(place):
    return ox.geocode(f"{place}, Berlin, Germany")


def find_place(name, label):
    try:
        return cached_geodata(name)
    except Exception:
        st.error(f"Couldn't find the {label} '{name}'. Try another name.")
        st.stop()


# Caching to avoid repeated graph loading
@st.cache_resource
def cached_graph(start, end):
    return load_graph(start, end)


st.title("Berlin Route Finder")

start_name = st.text_input("Start")
end_name = st.text_input("Destination")

if st.button("Find route"):
    if not start_name or not end_name:
        st.warning("Please enter both a start and a destination.")
        st.stop()

    start = find_place(start_name, "start")
    end = find_place(end_name, "destination")

    with st.spinner("Loading streets..."):
        G = cached_graph(start, end)

    route, distance = find_route(G, start, end)

    # Keep the route between reruns, otherwise the map flashes and disappears
    st.session_state["map"] = make_map(G, route, distance, start_name, end_name)
    st.session_state["distance"] = distance

if "map" in st.session_state:
    st.metric("Distance", f"{st.session_state['distance']:.0f} m")
    st_folium(st.session_state["map"], width=700, height=500, returned_objects=[])