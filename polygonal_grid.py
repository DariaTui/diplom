import osmnx as ox
import folium
import webbrowser
import geopandas as gpd
import pandas as pd
import h3pandas
from connect_bd import df_lat, df_lon, name_obj
import h3
from shapely.geometry import Polygon
#changes
# Ольхон и его границы
place = "остров Ольхон"
gdf = ox.geocode_to_gdf(place, which_result=1) 
olhon_hex = gdf.h3.polyfill_resample(8)

# создается dataFrame с переданными данными 
df_olkhon = pd.DataFrame({"lat": df_lat, "lng": df_lon, "name":name_obj})
# создается столбец h3_8
df_olkhon["h3_8"] = df_olkhon.apply(lambda row: h3.geo_to_h3(row["lat"], row["lng"], 8), axis=1)
# создается столбец object_count в котором подсчитывается кол-во объектов на полигон
df_olkhon['object_count'] = df_olkhon.groupby('h3_8')['name'].transform('count')
#создается столбец геометрии с данными полигонов
obj_hex = df_olkhon.h3.geo_to_h3_aggregate(8)

# Шаг 3: Удаляются дубликаты
obj_hex = df_olkhon[["h3_8","object_count"]].drop_duplicates()


obj_hex["geometry"] = obj_hex["h3_8"].apply(
    lambda h3_index: Polygon(h3.h3_to_geo_boundary(h3_index, geo_json=True))
)

obj_hex = gpd.GeoDataFrame(obj_hex, geometry="geometry", crs="EPSG:4326")

# # Джойним полигоны объектов и полигоны местности (сетки)
# sjoin_hex = gpd.sjoin(olhon_hex, obj_hex, how='left')

# # Считаем количество объектов в каждом гексагоне
# sjoin_hex['object_count'] = sjoin_hex.groupby('index')['index_right'].transform('count').fillna(0)

# Создаем карту
m = folium.Map([gdf.centroid.y, gdf.centroid.x])

# Функция для выбора цвета в зависимости от количества объектов
def get_color(count):
    if count > 1:
        return "red"  # Более яркий цвет для полигонов с >1 объектами
    elif count == 1:
        return "yellow"  # Нейтральный цвет для 1 объекта
    else:
        return "green"  # Стандартный цвет, если объектов нет

folium.GeoJson(olhon_hex, color="green").add_to(m)

for i,r in obj_hex.iterrows():# i = id , r = count_object(значению)
    folium.GeoJson(
        data=r["geometry"].__geo_interface__,
        style_function=lambda feature, count=r["object_count"]: {
            "color": get_color(count),
            "weight": 1,
            "fillOpacity": 0.5,
        },
        tooltip=f"Objects: {r['object_count']}"
    ).add_to(m)
    #print('i = ',i,' r = ',r["object_count"],' g = ',r["geometry"])

# Вывод маркеров мест на карту
for index, rows in df_olkhon.iterrows():
    folium.Marker(
        location=[rows["lat"], rows["lng"]],
        tooltip="Click me!",
        popup=rows["name"],
        icon=folium.Icon(icon="place_icon.png"),
    ).add_to(m)

# Сохраняем карту
m.save("map.html")
webbrowser.open("map.html")
