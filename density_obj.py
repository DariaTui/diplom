import folium.map
import osmnx as ox
import folium
import webbrowser
import geopandas as gpd
import pandas as pd
import h3pandas
import numpy as np
from shapely.geometry import Point
from analyze_data import minmax_normalize_data
#передача переменных из файла с выборкой данных из бд
from connect_bd import choose_obj

import h3
from shapely.geometry import Polygon

from map_create import create_maps

from matplotlib.colors import LogNorm
import matplotlib.cm as cm

type_obj = "accommodation_places"
size_poligon = 7
zoom=9
#тип который пользователь выберет как сферу бизнеса
type_business = ''

# Ольхон и его границы
place = "остров Ольхон"
gdf = ox.geocode_to_gdf(place, which_result=1) 
# Создаем карту
m = folium.Map([gdf.centroid.y, gdf.centroid.x])
olhon_hex = gdf.h3.polyfill_resample(size_poligon)
# достопримечатеельности

def create_geometry(df, size_poligon, full_hex):
    try:
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
    except:
        return obj_hex 

# Цветовые градиенты (можно изменить под себя)
COLOR_MAP = {
    "низкая": "#fecc5c",  # Оранжевый
    "средняя": "#ff6c56",  # Красный
    "высокая": "#bd0026"  # Темно-красный
}

# Логарифмическое распределение цветов
def get_color(value, min_val, max_val): 
    """Возвращает цвет на основе логарифмической шкалы с 3 уровнями."""
    
    norm = LogNorm(vmin=max(min_val, 1), vmax=max_val)  # Лог-нормализация
    thresholds = [
        min_val, 
        np.exp((np.log(min_val) + np.log(max_val)) / 2),  # Среднее геометрическое (центр шкалы)
        max_val
    ]

    if value <= thresholds[1]:
        return COLOR_MAP["низкая"]
    elif value <= thresholds[2]:
        return COLOR_MAP["средняя"]
    else:
        return COLOR_MAP["высокая"]


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

      <i style="background: #fecc5c; width: 20px; height: 10px; display: inline-block;"></i> Низкая плотность<br>
      <i style="background: #ff6c56; width: 20px; height: 10px; display: inline-block;"></i> Средняя плотность<br>
      <i style="background: #bd0026; width: 20px; height: 10px; display: inline-block;"></i> Высокая плотность<br>

    </div>
    '''
    map_object.get_root().html.add_child(folium.Element(legend_html))


# Основная функция карты
def main(df, gdf=gdf):
    full_hex = pd.DataFrame({"h3_8": olhon_hex.index})

    obj_hex = create_geometry(df, size_poligon, full_hex)
    
    if obj_hex.empty:
        return print("Данные не найдены. Возникла ошибка")

    min_count, max_count = obj_hex["object_count"].min(), obj_hex["object_count"].max()

    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=zoom)
    folium.GeoJson(olhon_hex, color="green").add_to(m)

    for _, row in obj_hex.iterrows():
        tooltip_text = f"количество объектов: {row['object_count']}"
        folium.GeoJson(
            data=row["geometry"].__geo_interface__,
            style_function=lambda feature, count=row["object_count"]: {
                "color": get_color(count, min_count, max_count),
                "weight": 1,
                "fillOpacity": 0.5,
            },
            tooltip=tooltip_text
        ).add_to(m)

    # легенда
    add_legend(m)

    return m

def markers_obj(map,df):
    # Вывод маркеров мест на карту
    for index, rows in df.iterrows():
        if df is "df_cat_olkhon":
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
        
        map.save("map.html")
        webbrowser.open("map.html")
    return map

# создается dataFrame с типами и выборка значений по выбранному типу бизнеса
def density_map_function(gdf=gdf, type_obj="", type_business="", price='', rating='', kitchen=''):
    df = choose_obj(type_obj)
    
    # Фильтрация данных в зависимости от типа объекта
    if type_obj == "public_eating":
        if type_business:
            
            df = df[df["type_business"].apply(lambda x: 
                type_business.strip().lower() in [i.strip().lower() for i in x] 
                if isinstance(x, list) 
                else x.strip().lower() == type_business.strip().lower()
            )]


        if price:
            try:
                min_price, max_price = map(float, price.split('-'))
                df = df[(df["price"] >= min_price) & (df["price"] <= max_price)]
            except ValueError:
                pass  # Если не удается разобрать цену, фильтрация не применяется
        if rating:
            try:
                min_rating, max_rating = map(float, rating.split('-'))
                df = df[(df["rating"] >= min_rating) & (df["rating"] <= max_rating)]
            except ValueError:
                pass  # Если не удается разобрать рейтинг, фильтрация не применяется
        if kitchen:
            # df = df[df["kitchen"].apply(lambda x: kitchen in x.split(',') if isinstance(x, str) else False)]
            df = df[df["kitchen"].apply(lambda x: 
                kitchen.strip().lower() in [i.strip().lower() for i in x.split(",")] 
                if isinstance(x, str) 
                else False
            )]

    
    elif type_obj == "accommodation_places":
        if price:
            try:
                min_price, max_price = map(float, price.split('-'))
                df = df[(df["price"] >= min_price) & (df["price"] <= max_price)]
            except ValueError:
                pass
        if rating:
            try:
                df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
                min_rating, max_rating = map(float, rating.split('-'))
                df = df[(df["rating"] >= min_rating) & (df["rating"] <= max_rating)]
            except ValueError:
                pass
    # landmarks фильтров не имеет, просто передаем df в main
    m = main(df, gdf)
    if m != "":
        return create_maps(f"{type_obj}_density.html", m)
    else:
        return print("Данные не найдены. Возникла ошибка")


density_map_function( 
    type_obj="landmarks", 
    type_business="", 
    price="", 
    rating="", 
    kitchen=""
)
