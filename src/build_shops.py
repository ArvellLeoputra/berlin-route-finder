import csv
import os

import osmnx as ox

from src.config import CENTER, RADIUS

KINDS = {
    "Post office": {"amenity": "post_office"},
    "Pharmacy": {"amenity": "pharmacy"},
    "Groceries": {"shop": "supermarket"},
    "Bakery": {"shop": "bakery"},
    "ATM": {"amenity": "atm"},
    "Drugstore": {"shop": "chemist"},
}

FILENAME = "data/shops.csv"


def main():
    os.makedirs("data", exist_ok=True)
    rows = []

    for kind, tags in KINDS.items():
        print(f"Downloading {kind}...")
        gdf = ox.features_from_point(CENTER, tags=tags, dist=RADIUS)

        count = 0
        for (element, id), row in gdf.iterrows():
            point = row.geometry.representative_point()
            lat, lon = point.y, point.x

            if ox.distance.great_circle(CENTER[0], CENTER[1], lat, lon) > RADIUS:
                continue

            name = row.get("name")
            if not isinstance(name, str):  # missing names come back as NaN
                name = ""

            rows.append({
                "kind": kind,
                "name": name,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "osm_id": f"{element}/{id}"
            })

            count += 1
        
        print(f" {count} found")

    with open(FILENAME, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["kind", "name", "lat", "lon", "osm_id"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {FILENAME} ({len(rows)} shops)")


if __name__ == "__main__":
    main()