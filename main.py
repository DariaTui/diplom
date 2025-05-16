import osmnx as ox
import folium
import webbrowser
import geopandas as gpd
import pandas as pd
import h3pandas
import numpy as np
from shapely.geometry import Point
from analyze_data import minmax_normalize_data, corr_data
from connect_bd import choose_obj

import h3
from shapely.geometry import Polygon
from map_create import create_maps
from shapely.ops import nearest_points
from shapely.geometry import Point
from pyproj import Transformer
from zoning_olkhon import gdfVec

business = 'общественное питание'
size_poligon = 8
zoom=9

place = "остров Ольхон"
gdf = ox.geocode_to_gdf(place, which_result=1)
m = folium.Map([gdf.centroid.y, gdf.centroid.x])

olhon_hex = gdf.h3.polyfill_resample(size_poligon)

transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

weights = {
    "other_object_count_score": 1,
    "distance_to_route_score": 1,
    "landmark_count_score": 1,
    "object_count_score": 1,
    "degree_landshaft_zone_score": 1
}

def load_routes():
    file_path = "C:/Users/User/Desktop/studyyy/diplom/coding/diplom/datas/qgis/routes_Baikal.geojson"
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
    elif z_score > 0.9:
        return "#960e05" #red
    elif z_score > 0.8:
        return "#f21000" #red
    elif z_score > 0.70:
        return "#f22c00" #red
    elif z_score > 0.60:
        return "#f24900" #red
    elif z_score > 0.4:
        return "#f27500" #red
    elif z_score == 0:
        return "gray"
    elif z_score < 0.30:
        return "#fff703" 
    else:
        return "#ffab03"

# Функция для генерации легенды
def add_legend(map_object):
    legend_html = '''
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        width: 180px;
        height: auto;
        background-color: white;
        z-index:9999;
        font-size:14px;
        padding: 10px;
        border: 2px solid grey;
        border-radius: 5px;
    ">
      <b>Легенда</b><br>
      <i style="background: #960e05; width: 20px; height: 10px; display: inline-block;"></i> КБС более 0.9<br>
      <i style="background: #f21000; width: 20px; height: 10px; display: inline-block;"></i> КБС более 0.8<br>
      <i style="background: #f22c00; width: 20px; height: 10px; display: inline-block;"></i> КБС более 0.7<br>
      <i style="background: #f24900; width: 20px; height: 10px; display: inline-block;"></i> КБС более 0.6<br>
      <i style="background: #f27500; width: 20px; height: 10px; display: inline-block;"></i> КБС более 0.4<br>
      <i style="background: #ffab03; width: 20px; height: 10px; display: inline-block;"></i> КБС более 0.3<br>
      <i style="background: #fff703; width: 20px; height: 10px; display: inline-block;"></i> КБС менее 0.3<br>
      <i style="background: grey; width: 20px; height: 10px; display: inline-block;"></i> Недоступная местность<br>

    </div>
    '''
    map_object.get_root().html.add_child(folium.Element(legend_html))

def main(df1, df2, gdf, weight_zone, business):

    full_hex = pd.DataFrame({"h3_8": olhon_hex.index})

    obj_hex1 = create_geometry(df1, size_poligon, full_hex)
    obj_hex2 = create_geometry(df2, size_poligon, full_hex)

    routes_gdf = load_routes()

    other_business = "общественное питание" if business == "места размещения" else "места размещения"

    obj_hex1["other_object_count"] = obj_hex1["h3_8"].map(obj_hex2.set_index("h3_8")["object_count"]).fillna(0)
    obj_hex1["distance_to_route"] = obj_hex1["geometry"].apply(lambda geom: calculate_distance_to_routes(geom, routes_gdf))
    obj_hex1["landmark_count"] = obj_hex1["geometry"].apply(lambda geom: calculate_landmarks_within_radius(geom, choose_obj("landmarks"), 2500))
    obj_hex1["degree_landshaft_zone"] = obj_hex1["geometry"].apply(lambda geom: calculate_degree_landshaft_zone(geom, gdfVec))

    normalization_data = pd.DataFrame({
        'object_count': obj_hex1['object_count'],
        'other_object_count': obj_hex1['other_object_count'],
        'distance_to_route': obj_hex1['distance_to_route'],
        'landmark_count': obj_hex1['landmark_count'],
        'degree_landshaft_zone': obj_hex1["degree_landshaft_zone"],
        'degree_favorability':0
    })

    for column in normalization_data.columns:
        obj_hex1[f"{column}_score"] = minmax_normalize_data(normalization_data[column].values, column_name=column)

    # Подсчет коэффициента благоприятствования
    obj_hex1["degree_favorability_score"] = (
        (obj_hex1["other_object_count_score"] * weight_zone["other_object_count_score"]) -
        (obj_hex1["distance_to_route_score"] * weight_zone["distance_to_route_score"]) +
        (obj_hex1["landmark_count_score"] * weight_zone["landmark_count_score"]) -
        (obj_hex1["object_count_score"] * weight_zone["object_count_score"])
    ) * (obj_hex1["degree_landshaft_zone_score"] * weight_zone["degree_landshaft_zone_score"])

    #нормализация КБС
    obj_hex1["degree_favorability_score"]=minmax_normalize_data(obj_hex1["degree_favorability_score"].values,column_name="degree_favorability_score")

    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=zoom)
    folium.GeoJson(olhon_hex, color="green").add_to(m)

    for _, row in obj_hex1.iterrows():
        tooltip_text = (f"{business}: {row['object_count']}<br>"
                        f"{other_business}: {int(row['other_object_count'])} (Z: {row['other_object_count_score']:.2f})<br>\n"
                        f"Расстояние до ближайшего маршрута: {row['distance_to_route']:.2f} м (Z: {row['distance_to_route_score']:.2f})<br>\n"
                        f"Достопримечательности в радиусе 2.5 км: {row['landmark_count']} (Z: {row['landmark_count_score']:.2f})")
        folium.GeoJson(
            data=row["geometry"].__geo_interface__,
            style_function=lambda feature, z=row["degree_favorability_score"]: {
                "color": get_color(z),
                "weight": 1,
                "fillOpacity": 0.5,
            },
            tooltip=tooltip_text
        ).add_to(m)
        # легенда
    add_legend(m)
    return m

def filter_type(weights, gdf=gdf, business="public_eating"):
    df1 = choose_obj(business)
    df2 = choose_obj("public_eating" if business == "accommodation_places" else "accommodation_places")
    m = main(df1, df2, gdf, weights, business)
    file_html = create_maps("kbs_map.html", m)
    return file_html

filter_type(weights=weights)