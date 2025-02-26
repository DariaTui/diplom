import geopandas as gpd
import osmnx as ox
import folium
import webbrowser


prefer_tourism = {1:"историко-культурного и сакрального туризма",
                  2:"познавательного и экстремального вида туризма",
                  3:"сельского, познавательного и экстремальных видов туризма",
                  4:"обслуживания посетителей, пляжного и познавательного туризма",
                  5:"научного и познавательного туризма",
                  6:"пешего туризма по лесным тропам",
                  7:"активного спортивного и познавательного туризма"}
# Загрузка слоя
gdfVec = gpd.read_file("datas/qgis/zone_landshaft_Olkhon.geojson")
gdfVec = gdfVec.to_crs(epsg=4326)
# Вывод первых строк для проверки
print(gdfVec.head())

# Получаем координаты острова Ольхон через OSMnx
place = "остров Ольхон"
gdf = ox.geocode_to_gdf(place, which_result=1)

# Центр карты (берем первую точку)
m = folium.Map([gdf.centroid.y, gdf.centroid.x], zoom_start=10)

# Определение цветов
color_map = {1: "red", 2: "yellow", 3: "green"}

# Добавление полигонов на карту
for _, row in gdfVec.iterrows():
    zone_number = row["number"]  # Получаем номер зоны
    tooltip_text = prefer_tourism.get(zone_number, "Неизвестная зона")  # Получаем текст для tooltip
    
    color = color_map.get(row["degree"], "gray")  # Цвет по степени важности

    folium.GeoJson(
        row["geometry"].__geo_interface__,
        style_function=lambda feature, color=color: {
            "fillColor": color,
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5
        },
        tooltip=tooltip_text  # Добавляем всплывающую подсказку
    ).add_to(m)

# Сохранение и открытие карты
# m.save("mapVector.html")
# webbrowser.open("mapVector.html")

def create_zone_map():
    m = folium.Map([gdf.geometry.centroid.y.iloc[0], gdf.geometry.centroid.x.iloc[0]], zoom_start=10)

    for _, row in gdfVec.iterrows():
        zone_number = row["number"]
        zone_name = row["name"]
        color = color_map.get(row["degree"], "gray")
    
        folium.GeoJson(
            row["geometry"].__geo_interface__,
            style_function=lambda feature, color=color: {
                "fillColor": color,
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.5
            },
            tooltip=zone_name
        ).add_to(m)

    m.save("zone_map.html")
    webbrowser.open("zone_map.html")

# Запуск функции создания карты с зонами
create_zone_map()


# код создает гексагональную карту и закрашивает полигоны в зависисмости с их местонахождением
import osmnx as ox
import folium
import webbrowser
import geopandas as gpd
import pandas as pd
import h3
import numpy as np
from shapely.geometry import Polygon
import osmnx as ox
import folium
import webbrowser
import geopandas as gpd
import pandas as pd
import h3pandas
from shapely.geometry import Point

# Загрузка зон острова Ольхон
gdf_zones = gpd.read_file("datas/qgis/zone_landshaft_Olkhon.geojson").to_crs(epsg=4326)

# Получение границ острова Ольхон
place = "остров Ольхон"
gdf = ox.geocode_to_gdf(place, which_result=1)

# Цвета зон (по degree)
color_map = {1: "red", 2: "yellow", 3: "green", 4: "blue", 5: "purple", 6: "orange", 7: "pink"}

# 🔹 **Создание гексагональной сетки**
olhon_hex = gdf.h3.polyfill_resample(8)
m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=10)

# 🔹 **Закраска гексагонов по зонам**
for _, row in olhon_hex.iterrows():
    hex_geometry = row["geometry"]  # Граница гексагона
    hex_color = "gray"  # По умолчанию серый
    zone_name = "Неизвестная зона"
    zone_number = ""
    tooltip_text = ""
    for _, zone in gdf_zones.iterrows():
        if hex_geometry.intersects(zone["geometry"]):  # Проверяем пересечение с зоной
            hex_color = color_map.get(zone["degree"], "gray")
            zone_name = zone["name"]
            zone_number = zone["number"]
            tooltip_text = prefer_tourism.get(zone_number, "Неизвестная зона")
            break  # Берем первую найденную зону

    folium.GeoJson(
        data=hex_geometry.__geo_interface__,
        style_function=lambda feature, color=hex_color: {
            "fillColor": color,
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5
        },
        tooltip=tooltip_text
    ).add_to(m)

# 🔹 **Сохранение и открытие карты**
m.save("map/hexagonal_zones.html")
webbrowser.open("map/hexagonal_zones.html")
