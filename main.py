import osmnx as ox
import folium
import webbrowser
import geopandas as gpd
import pandas as pd
import h3pandas
import numpy as np
from shapely.geometry import Point
from analyze_data import z_normalize_data, minmax_normalize_data, corr_data
from connect_bd import df_id, df_lat, df_lon, name_obj, type_obj
from connect_bd import df_cat_id, df_cat_lat, df_cat_lon, name_cat_obj, type_cat_obj, df_cat_pros, df_cat_cons
from connect_bd import df_pl_id, df_pl_lat, df_pl_lon, name_pl_obj, df_pl_pros, df_pl_cons
import h3
from shapely.geometry import Polygon
from map_create import create_maps
from shapely.ops import nearest_points
from shapely.geometry import Point
from pyproj import Transformer
from zoning_olkhon import gdfVec

business = 'общественное питание'
size_poligon = 7
place = "остров Ольхон"
gdf = ox.geocode_to_gdf(place, which_result=1)
m = folium.Map([gdf.centroid.y, gdf.centroid.x])
olhon_hex = gdf.h3.polyfill_resample(size_poligon)
df_landmark_olkhon = pd.DataFrame({"id": df_id, "lat": df_lat, "lng": df_lon, "name": name_obj})

transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

weights = [1,1,1,1,1]

def load_routes():
    file_path = "datas/qgis/routes_Baikal.geojson"
    return gpd.read_file(file_path)

def calculate_distance_to_routes(polygon, routes_gdf):
    nearest_distance = float("inf")
    for _, route in routes_gdf.iterrows():
        nearest_point = nearest_points(polygon.centroid, route.geometry)[1]
        distance = polygon.centroid.distance(nearest_point)
        if distance < nearest_distance:
            nearest_distance = distance
    return nearest_distance

def calculate_landmarks_within_radius(polygon, df_landmark, radius):
    count = 0
    polygon_centroid = transformer.transform(polygon.centroid.x, polygon.centroid.y)
    for _, row in df_landmark.iterrows():
        point = transformer.transform(row["lng"], row["lat"])
        distance = ((polygon_centroid[0] - point[0])**2 + (polygon_centroid[1] - point[1])**2)**0.5
        if distance <= radius:
            count += 1
    return count

# Функция для определения степени природоохранных ограничений по пересечению
def calculate_degree_landshaft_zone(polygon, gdfVec):
    for _, zone in gdfVec.iterrows():
        if polygon.intersects(zone["geometry"]):
            return zone["degree"]  # Возвращаем степень природоохранных ограничений
    return 3  # Если не попал ни в одну зону, то минимальные ограничения


def create_geometry(df, size_poligon, full_hex):
    if len(df) > 0:
        df["h3_8"] = df.apply(lambda row: h3.geo_to_h3(row["lat"], row["lng"], size_poligon), axis=1)
        df["object_count"] = df.groupby("h3_8")["name"].transform("count")
        obj_hex = df[["h3_8", "object_count"]].drop_duplicates()
    else:
        obj_hex = pd.DataFrame(columns=["h3_8", "object_count"])

    # Собираем ВСЕ ячейки H3
    all_hex = pd.concat([full_hex, pd.DataFrame({"h3_8": df["h3_8"].unique()})]).drop_duplicates()

    # Объединяем полную сетку с объектами
    obj_hex = pd.merge(all_hex, obj_hex, on="h3_8", how="left").fillna(0)

    # Преобразуем ячейки в полигоны
    obj_hex["geometry"] = obj_hex["h3_8"].apply(lambda h3_index: Polygon(h3.h3_to_geo_boundary(h3_index, geo_json=True)))

    return obj_hex

def get_color(z_score):
    if pd.isna(z_score):
        return "gray"  # Серые полигоны для пустых ячеек
    elif z_score > 0.6:
        return "red"
    elif z_score == 0:
        return "gray"
    elif z_score < 0.3:
        return "yellow"
    else:
        return "green"


def main(df1, df2, gdf):
    full_hex = pd.DataFrame({"h3_8": olhon_hex.index})

    obj_hex1 = create_geometry(df1, size_poligon, full_hex)
    obj_hex2 = create_geometry(df2, size_poligon, full_hex)

    routes_gdf = load_routes()

    other_business = 'общественное питание' if business == 'места размещения' else 'места размещения'

    obj_hex1["other_object_count"] = obj_hex1["h3_8"].map(obj_hex2.set_index("h3_8")["object_count"]).fillna(0)
    obj_hex1["distance_to_route"] = obj_hex1["geometry"].apply(lambda geom: calculate_distance_to_routes(geom, routes_gdf))
    obj_hex1["landmark_count"] = obj_hex1["geometry"].apply(lambda geom: calculate_landmarks_within_radius(geom, df_landmark_olkhon, 2500))
    obj_hex1["degree_landshaft_zone"] = obj_hex1["geometry"].apply(lambda geom: calculate_degree_landshaft_zone(geom, gdfVec))


    # Формируем таблицу для нормализации
    normalization_data = pd.DataFrame({
        'object_count': obj_hex1['object_count'],
        'other_object_count': obj_hex1['other_object_count'],
        'distance_to_route': obj_hex1['distance_to_route'],
        'landmark_count': obj_hex1['landmark_count'],
        'degree_landshaft_zone': obj_hex1["degree_landshaft_zone"],
        'degree_favorability':0
    })
    #normalization_data = minmax_normalize_data(normalization_data)
    
    # Применяем нормализацию ко всем столбцам
        # Применяем нормализацию ко всем столбцам
    for column in normalization_data.columns:

        obj_hex1[f"{column}_z_score"] = minmax_normalize_data(normalization_data[column].values, column_name=column)


        
    # Подсчет коэффициента благоприятствования
    obj_hex1["degree_favorability_z_score"] = (
            obj_hex1["other_object_count_z_score"] +
            obj_hex1["distance_to_route_z_score"] +
            obj_hex1["landmark_count_z_score"] -
            obj_hex1["object_count_z_score"]
    ) * obj_hex1["degree_landshaft_zone_z_score"]

    #нормализация КБС
    obj_hex1["degree_favorability_z_score"]=minmax_normalize_data(obj_hex1["degree_favorability_z_score"].values,column_name="degree_favorability_z_score")

    # Заполняем в таблице normalization_data
    normalization_data["degree_favorability"] = obj_hex1["degree_favorability_z_score"] 
    #print(min(obj_hex1["degree_favorability_z_score"]), max(obj_hex1["degree_favorability_z_score"]))

    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=size_poligon)
    folium.GeoJson(olhon_hex, color="green").add_to(m)

    for _, row in obj_hex1.iterrows():
        tooltip_text = (f"{business}: {row['object_count']}"
                        f"{other_business}: {int(row['other_object_count'])} (Z: {row['other_object_count_z_score']:.2f})\n"
                        f"Расстояние до ближайшего маршрута: {row['distance_to_route']:.2f} м (Z: {row['distance_to_route_z_score']:.2f})\n"
                        f"Достопримечательности в радиусе 2.5 км: {row['landmark_count']} (Z: {row['landmark_count_z_score']:.2f})")
        folium.GeoJson(
            data=row["geometry"].__geo_interface__,
            style_function=lambda feature, z=row["degree_favorability_z_score"]: {
                "color": get_color(z),
                "weight": 1,
                "fillOpacity": 0.5,
            },
            tooltip=tooltip_text
        ).add_to(m)
    return m

def choose_business(business):
    if business == 'общественное питание':
        return pd.DataFrame({"id": df_cat_id, "lat": df_cat_lat, "lng": df_cat_lon, "name": name_cat_obj, "pros": df_cat_pros, "cons": df_cat_cons})
    if business == "места размещения":
        return pd.DataFrame({"id": df_pl_id, "lat": df_pl_lat, "lng": df_pl_lon, "name": name_pl_obj, "pros": df_pl_pros, "cons": df_pl_cons})

def filter_type(gdf, business):
    df1 = choose_business(business)
    df2 = choose_business("общественное питание" if business == "места размещения" else "места размещения")
    m = main(df1, df2, gdf)
    create_maps("map.html", m)

filter_type(gdf, business)
