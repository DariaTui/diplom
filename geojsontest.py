# import folium
# import json
# import webbrowser
# from polygonal_grid import markers_obj

# # Путь к вашему файлу geojson
# file_path = "datas/routes_Baikal.geojson"
# file_path_OOP = "datas/OOPT_BP.geojson"
# #файл для сохранения и вывода карты
# file_name = "map_routes.html"
# # Чтение GeoJSON
# with open(file_path, 'r', encoding='utf-8') as file:
#     geojson_data = json.load(file)

# #file_OOP = 

# # Создание базовой карты
# m = folium.Map(location=[53.1036586, 107.3496115], zoom_start=9)

# # Добавление GeoJSON-данных на карту
# folium.GeoJson(geojson_data).add_to(m)

# # Сохранение карты в файл и открытие в браузере
# markers = markers_obj(m)
# markers.save(file_name)
# m.save(file_name)
# print("Карта сохранена в map_routes.html. Откройте файл в браузере.")
# webbrowser.open(file_name)


import folium

import osmnx as ox
from shapely.geometry import Point, Polygon

# Шаг 1: Получение данных об аэропортах и других объектах через OSM
def get_restricted_areas():
    # Определяем bounding box для области поиска (широта и долгота)
    location = "Olkhon, Russia"  # Измените на нужный город
    #tags = {'aeroway': ['aerodrome', 'helipad']}  # Фильтруем аэропорты и вертолетные площадки
    tags = {'amenity': ['school', 'hospital',"bar", 'shop']}
    gdf = ox.geometries_from_place(location, tags)
    return gdf

# Шаг 2: Отобразить зоны ограничений на карте
def plot_map(restricted_areas):
    # Инициализация карты
    m = folium.Map(location=[53.1036586, 107.3496115], zoom_start=10)  # Москва, Россия
    
    # Добавление зон ограничений
    for _, area in restricted_areas.iterrows():
        if 'geometry' in area and isinstance(area.geometry, Polygon):
            folium.Polygon(
                locations=[(lat, lon) for lon, lat in area.geometry.exterior.coords],
                color='red',
                fill=True,
                fill_opacity=0.4,
                tooltip=area.get('name', 'Restricted Zone')
            ).add_to(m)
        elif 'geometry' in area and isinstance(area.geometry, Point):
            folium.Marker(
                location=[area.geometry.y, area.geometry.x],
                popup=area.get('name', 'Restricted Zone'),
                icon=folium.Icon(color='red')
            ).add_to(m)

    return m

# Шаг 3: Основной процесс
restricted_areas = get_restricted_areas()
print(restricted_areas)
map_with_restrictions = plot_map(restricted_areas)

# Сохранение карты в файл
map_with_restrictions.save("restricted_areas_map.html")
import webbrowser
webbrowser.open("restricted_areas_map.html")
