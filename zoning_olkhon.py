import geopandas as gpd
import osmnx as ox
import folium
import webbrowser
from map_create import create_maps
gdfVec = gpd.read_file("datas/qgis/zone_landshaft_Olkhon.geojson")
gdfVec = gdfVec.to_crs(epsg=4326)

def zone_olkhon():
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

    # Получаем координаты острова Ольхон через OSMnx
    place = "остров Ольхон"
    gdf = ox.geocode_to_gdf(place, which_result=1)

    # Центр карты (берем первую точку)
    m = folium.Map([gdf.centroid.y, gdf.centroid.x], zoom_start=10)

    # Определение цветов
    color_map = {1: "#006400", 2: "#FF4500", 3: "#9ACD32", 4:"#CD5C5C",5:"#556B2F",6:"#90EE90",7:"#F0E68C"}

    # Добавление полигонов на карту
    for _, row in gdfVec.iterrows():
        zone_number = row["number"]  # Получаем номер зоны
        tooltip_text = prefer_tourism.get(zone_number, "Неизвестная зона")  # Получаем текст для tooltip
        color = color_map.get(row["number"], "gray")  # Цвет по степени важности

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
    return m


