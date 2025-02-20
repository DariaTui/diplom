import geopandas as gpd
import osmnx as ox
import folium
import webbrowser

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

# Добавление полигонов
for _, row in gdfVec.iterrows():
    color = color_map.get(row["degree"], "gray")  # Серый цвет по умолчанию

    folium.GeoJson(
        row["geometry"].__geo_interface__,  # Преобразуем в формат GeoJSON
        style_function=lambda feature, color=color: {
            "fillColor": color,
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5
        }
    ).add_to(m)

# Сохранение и открытие карты
m.save("mapVector.html")
webbrowser.open("mapVector.html")
