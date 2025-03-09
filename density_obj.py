import osmnx as ox
import folium
import webbrowser
import geopandas as gpd
import pandas as pd
import h3pandas
from shapely.geometry import Point
from analyze_data import z_normalize_data
#передача переменных из файла с выборкой данных из бд
from connect_bd import df_id, df_lat, df_lon, name_obj, type_obj
from connect_bd import df_cat_id, df_cat_lat, df_cat_lon, name_cat_obj, type_cat_obj, df_cat_pros, df_cat_cons
from connect_bd import df_pl_id, df_pl_lat, df_pl_lon, name_pl_obj,df_pl_pros, df_pl_cons

import h3
from shapely.geometry import Polygon

from map_create import create_maps


type_obj = "public_eating"
size_poligon = 7
#тип который пользователь выберет как сферу бизнеса
type_business = ''

# Ольхон и его границы
place = "остров Ольхон"
gdf = ox.geocode_to_gdf(place, which_result=1) 
# Создаем карту
m = folium.Map([gdf.centroid.y, gdf.centroid.x])

olhon_hex = gdf.h3.polyfill_resample(size_poligon)
# достопримечатеельности
df_landmark_olkhon = pd.DataFrame({"id":df_id,"lat": df_lat, "lng": df_lon, "name":name_obj})

# Фильтрация объектов, чтобы оставить только те, что находятся внутри границ Ольхона
# def filter_points_within_island(df, gdf):
#     island_polygon = gdf.geometry.iloc[0]  # Полигон острова Ольхон
#     df["geometry"] = df.apply(lambda row: Point(row["lng"], row["lat"]), axis=1)  # Создание геометрии
#     df_filtered = df[df["geometry"].apply(lambda point: point.within(island_polygon))]  # Фильтрация
#     return df_filtered.drop(columns=["geometry"])  # Удаляем колонку с геометрией

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

# Функция для выбора цвета в зависимости от количества объектов
def get_color(z_score):
    if z_score > 1.5:
        return "red"  # Высокая концентрация объектов
    elif z_score > 0.5:
        return "orange"  # Средняя концентрация
    elif z_score > -0.5:
        return "yellow"  # Небольшая концентрация
    else:
        return "green"  # Низкая концентрация


def main(df, gdf=gdf):
    full_hex = pd.DataFrame({"h3_8": olhon_hex.index})

    obj_hex = create_geometry(df, size_poligon, full_hex)
    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=size_poligon)
    folium.GeoJson(olhon_hex, color="green").add_to(m)

    for _, row in obj_hex.iterrows():
        tooltip_text = (f"{type_obj}: {row['object_count']}")
        folium.GeoJson(
            data=row["geometry"].__geo_interface__,
            style_function=lambda feature, count=row['object_count']: {
                "color": get_color(count),
                "weight": 1,
                "fillOpacity": 0.5,
            },
            tooltip=tooltip_text
        ).add_to(m)
    return m


def markers_obj(map,df):
    # Вывод маркеров мест на карту
    for index, rows in df.iterrows():
        if df is "df_cat_olkhon": #or df == df_pl_olkhon:
            popup_text = f"""
            <b>{rows["name"]}</b><br>
            <b>Плюсы:</b> {rows["pros"] if pd.notna(rows["pros"]) else "Нет данных"}<br>
            <b>Минусы:</b> {rows["cons"] if pd.notna(rows["cons"]) else "Нет данных"}
            """
            folium.Marker(
                location=[rows["lat"], rows["lng"]],
                tooltip="Click me!",
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(icon="place_icon.png"),
            ).add_to(map)
        else:
            folium.Marker(
                location=[rows["lat"], rows["lng"]],
                tooltip="Click me!",
                popup=folium.Popup(rows["name"], max_width=300),
                icon=folium.Icon(icon="place_icon.png"),
            ).add_to(map)
        
        #map.save("map.html")
        #webbrowser.open("map.html")
    return map

#IMPORTANT
# if __name__== '__main__':
#   markers_obj(m,df_cat_olkhon)
#   main(df_cat_olkhon)
#   webbrowser.open("map.html")

 # определение выборки по бизнесу(общепит, места размещения и тд)
def choose_obj(type_obj): 
    if type_obj == "public_eating":
        # создается dataFrame с переданными данными caterings
        return pd.DataFrame({"id":df_cat_id, "lat": df_cat_lat, "lng": df_cat_lon, "name":name_cat_obj, "pros":df_cat_pros, "cons":df_cat_cons})
    if type_obj == "accommodation_places":
        return pd.DataFrame({"id":df_pl_id, "lat": df_pl_lat, "lng": df_pl_lon, "name":name_pl_obj, "pros":df_pl_pros, "cons":df_pl_cons})
    if type_obj == "landmarks":
        return pd.DataFrame({"id":df_id,"lat": df_lat, "lng": df_lon, "name":name_obj})


# создается dataFrame с типами и выборка значений по выбранному типу бизнеса
def density_map_function(gdf=gdf, type_obj="", type_business=""):
    df = choose_obj(type_obj)
    if type_business!='':
        df_type = pd.DataFrame({"type":type_obj}) 
        filtered_df = df_type[df_type['type'].apply(lambda x: type_business in x if isinstance(x, list) else x == type_business)]
        indexes = filtered_df.index #получение индексов заданных типов
        filter_df = df.loc[indexes] #поиск мест размещение с соответсвующим типу индексом
        
        m = main(filter_df,gdf)
        #m = markers_obj(m, df_landmark_olkhon)
        #m = create_routes()
        return create_maps(f"{type_obj}_density.html",m)
        # webbrowser.open("static\\"+f"{type_obj}_density.html")
    else:        
        m = main(df,gdf)
        #m = markers_obj(m, df_landmark_olkhon)
        #m = create_routes(m)
        return create_maps(f"{type_obj}_density.html",m)
        # webbrowser.open("static\\"+f"{type_obj}_density.html")
    
    
#print(filter_type(df_olkhon,type_obj, type_business,m))
#print(filter_type(df_pl_olkhon,gdf,type_obj,type_business,m))
density_map_function(gdf=gdf,type_obj=type_obj,type_business="")

