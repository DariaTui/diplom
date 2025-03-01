import osmnx as ox
import folium
import webbrowser
import geopandas as gpd
import pandas as pd
import h3pandas
from shapely.geometry import Point
from analyze_data import normalize_data
from connect_bd import df_id, df_lat, df_lon, name_obj
from connect_bd import df_cat_id, df_cat_lat, df_cat_lon, name_cat_obj, type_cat_obj, df_cat_pros, df_cat_cons
from connect_bd import df_pl_id, df_pl_lat, df_pl_lon, name_pl_obj, df_pl_pros, df_pl_cons
import h3
from shapely.geometry import Polygon
from map_create import create_maps

business = 'места размещения'
size_poligon = 7
place = "остров Ольхон"
gdf = ox.geocode_to_gdf(place, which_result=1)
m = folium.Map([gdf.centroid.y, gdf.centroid.x])
olhon_hex = gdf.h3.polyfill_resample(size_poligon)
df_landmark_olkhon = pd.DataFrame({"id": df_id, "lat": df_lat, "lng": df_lon, "name": name_obj})

def create_geometry(df, size_poligon):
    df["h3_8"] = df.apply(lambda row: h3.geo_to_h3(row["lat"], row["lng"], size_poligon), axis=1)
    df['object_count'] = df.groupby('h3_8')['name'].transform('count')
    obj_hex = df.h3.geo_to_h3_aggregate(size_poligon)
    obj_hex = df[["h3_8", "object_count"]].drop_duplicates()
    obj_hex["geometry"] = obj_hex["h3_8"].apply(lambda h3_index: Polygon(h3.h3_to_geo_boundary(h3_index, geo_json=True)))
    return obj_hex

def get_color(z_score):
    if z_score > 1.5:
        return "red"
    elif z_score > 0.5:
        return "orange"
    elif z_score > -0.5:
        return "yellow"
    else:
        return "green"

def main(df1, df2, gdf):
    obj_hex1 = create_geometry(df1, size_poligon)
    obj_hex2 = create_geometry(df2, size_poligon)

    other_business = 'общественное питание' if business == 'места размещения' else 'места размещения'

    obj_hex1["other_object_count"] = obj_hex1["h3_8"].map(obj_hex2.set_index("h3_8")["object_count"]).fillna(0)
    obj_hex1["z_score"] = normalize_data(obj_hex1["object_count"])

    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=size_poligon)
    folium.GeoJson(olhon_hex, color="green").add_to(m)

    for _, row in obj_hex1.iterrows():
        tooltip_text = (f"{business}: {row['object_count']}\n"
                        f"{other_business}: {int(row['other_object_count'])} (Z: {row['z_score']:.2f})")
        folium.GeoJson(
            data=row["geometry"].__geo_interface__,
            style_function=lambda feature, z=row["z_score"]: {
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
