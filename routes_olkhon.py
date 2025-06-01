import osmnx as ox
import folium
import networkx as nx
import webbrowser
import geopandas as gpd
from shapely.wkt import loads
from density_obj import df_olkhon, place, m 
from map_create import create_maps

file_name = "map_routes.html"

def create_routes():
    file_path = "datas/qgis/routes_Baikal.geojson"
    gdf_routes = gpd.read_file(file_path)
    # Добавляем маршруты на карту
    for _, row in gdf_routes.iterrows():
        geo_json = folium.GeoJson(row['geometry'], name=f"Route {_}")
        geo_json.add_to(m)

    return m
create_maps(file_name,m)