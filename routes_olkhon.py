import osmnx as ox
import folium
import networkx as nx
import webbrowser
import geopandas as gpd
from shapely.wkt import loads
from polygonal_grid import df_olkhon, place, m 

file_path = "../datas/routes_Baikal.geojson"
file_name = "map_routes.html"

gdf_routes = gpd.read_file(file_path)

# Добавляем маршруты на карту
for _, row in gdf_routes.iterrows():
    geo_json = folium.GeoJson(row['geometry'], name=f"Route {_}")
    geo_json.add_to(m)



m.save(file_name)
webbrowser.open(file_name)