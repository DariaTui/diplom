

#-----------------------------
import folium
import json
import webbrowser
import pandas as pd
import geopandas as gpd
import pyproj
#from polygonal_grid import markers_obj

m = folium.Map(location=[53.1036586, 107.3496115], zoom_start=9)

# Путь к вашему файлу geojson
file_path = "../datas/routes_Baikal.geojson"
file_path_OOPT = "../datas/OOPT_BPT.geojson"
#файл для сохранения и вывода карты
file_name = "map_routes.html"

input_proj = pyproj.Proj(init="epsg:3395")  # Укажите исходную проекцию данных (например, UTM)
output_proj = pyproj.Proj(init="epsg:4326")  # WGS84 (широта, долгота)

# Чтение GeoJSON
gdf_OOPT = gpd.read_file(file_path_OOPT) #заповедники GeoDataFrame заповедников(перечисление заповедников с координатами и др данными)
center = gdf_OOPT.centroid.iloc[0].coords[0]

#цикл нанесение OOPT зон

for index, row in gdf_OOPT.iterrows():
    
    #получение строки с координатми multipolygon из файла
    polygon = gdf_OOPT.iloc[index]["geometry"]
    # Преобразуем координаты из исходной системы в WGS84
    
    for polygon in polygon.geoms:
        locations = [(lat, lon) for lon, lat in polygon.exterior.coords]
        # Получаем координаты внешнего контура полигона
        coords = polygon.exterior.coords

        # Преобразуем каждый пункт координат в WGS84
        locations = []
        for lon, lat in coords:
            lon_wgs84, lat_wgs84 = pyproj.transform(input_proj, output_proj, lon, lat)
            locations.append((lat_wgs84, lon_wgs84))  # Добавляем в формате (широта, долгота)
    
        # Выводим преобразованные координаты
    folium.Polygon(locations=locations, color="grey", weight=2.5, opacity=1, fill=True, fill_opacity=0.3).add_to(m)


m.save("restricted_areas_map.html")
webbrowser.open("restricted_areas_map.html")

#--------------------------------------------------

#Получение данных об объектах c OSMNX
# import folium
# import osmnx as ox
# from shapely.geometry import Point, Polygon

# # Шаг 1: Получение данных об аэропортах и других объектах через OSM
# def get_restricted_areas():
#     # Определяем bounding box для области поиска (широта и долгота)
#     location = "Olkhon, Russia"  # Измените на нужный город
#     tags = {'aeroway': ['aerodrome', 'helipad']}  # Фильтруем аэропорты и вертолетные площадки
#     #tags = {'amenity': ['school', 'hospital']}
#     gdf = ox.geometries_from_place(location, tags)
#     return gdf

# # Шаг 2: Отобразить зоны ограничений на карте
# def plot_map(restricted_areas):
#     # Инициализация карты
#     m = folium.Map(location=[53.1036586, 107.3496115], zoom_start=10)  # Москва, Россия
    
#     # Добавление зон ограничений
#     for _, area in restricted_areas.iterrows():
#         if 'geometry' in area and isinstance(area.geometry, Polygon):
#             folium.Polygon(
#                 locations=[(lat, lon) for lon, lat in area.geometry.exterior.coords],
#                 color='red',
#                 fill=True,
#                 fill_opacity=0.4,
#                 tooltip=area.get('name', 'Restricted Zone')
#             ).add_to(m)
#         elif 'geometry' in area and isinstance(area.geometry, Point):
#             folium.Marker(
#                 location=[area.geometry.y, area.geometry.x],
#                 popup=area.get('name', 'Restricted Zone'),
#                 icon=folium.Icon(color='red')
#             ).add_to(m)

#     return m

# # Шаг 3: Основной процесс
# restricted_areas = get_restricted_areas()
# print(restricted_areas)
# map_with_restrictions = plot_map(restricted_areas)

# # Сохранение карты в файл
# map_with_restrictions.save("restricted_areas_map.html")
# import webbrowser
# webbrowser.open("restricted_areas_map.html")


