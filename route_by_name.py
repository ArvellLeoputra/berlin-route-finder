import osmnx as ox
from routing import load_graph, find_route, make_map

def prompt_location(prompt):
    while True:
        name = input(prompt)
        try:
            return name, ox.geocode(f"{name}, Berlin, Germany")
        except Exception:
            print(f"Couldn't find '{name}'. Try another name.")
            

start_name, start = prompt_location("Start: ")
end_name, end = prompt_location("Destination: ")

print("Loading streets...")
G = load_graph(start, end)

route, distance = find_route(G, start, end)
print(f"Distance: {distance:.0f} m")

m = make_map(G, route, distance, start_name, end_name)
m.save("route.html")
print("Saved route.html")