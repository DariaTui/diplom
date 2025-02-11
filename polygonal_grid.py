import osmnx as ox
import folium
import webbrowser
import geopandas as gpd
import pandas as pd
import h3pandas
#передача переменных из файла с выборкой данных из бд
from connect_bd import df_id, df_lat, df_lon, name_obj, type_obj
from connect_bd import df_cat_id, df_cat_lat, df_cat_lon, name_cat_obj, type_cat_obj

import h3
from shapely.geometry import Polygon

#тип который пользователь выберет как сферу бизнеса
type_business = 'Кофейня'

# Ольхон и его границы
place = "остров Ольхон"
gdf = ox.geocode_to_gdf(place, which_result=1) 
# Создаем карту
m = folium.Map([gdf.centroid.y, gdf.centroid.x])

olhon_hex = gdf.h3.polyfill_resample(8)
# создается dataFrame с переданными данными объектов инфраструктуры
df_olkhon = pd.DataFrame({"id":df_id,"lat": df_lat, "lng": df_lon, "name":name_obj})
# создается dataFrame с переданными данными caterings
df_cat_olkhon = pd.DataFrame({"id":df_cat_id, "lat": df_cat_lat, "lng": df_cat_lon, "name":name_cat_obj})



def create_geometry(df):
    # создается столбец h3_8
    df["h3_8"] = df.apply(lambda row: h3.geo_to_h3(row["lat"], row["lng"], 8), axis=1)
    # создается столбец object_count в котором подсчитывается кол-во объектов на полигон
    df['object_count'] = df.groupby('h3_8')['name'].transform('count')
    #создается столбец геометрии с данными полигонов
    obj_hex = df.h3.geo_to_h3_aggregate(8)

    # Шаг 3: Удаляются дубликаты
    obj_hex = df[["h3_8","object_count"]].drop_duplicates()


    obj_hex["geometry"] = obj_hex["h3_8"].apply(
        lambda h3_index: Polygon(h3.h3_to_geo_boundary(h3_index, geo_json=True))
    )
    return obj_hex

# Функция для выбора цвета в зависимости от количества объектов
def get_color(count):
    if count > 1:
        return "red"  # Более яркий цвет для полигонов с > 1 объектами
    elif count == 1:
        return "yellow"  # Нейтральный цвет для 1 объекта
    else:
        return "green"  # Стандартный цвет, если объектов нет

def main(df):

    folium.GeoJson(olhon_hex, color="green").add_to(m)
    obj_hex = create_geometry(df)
    # Находим соседние полигоны в olhon_hex и окрашиваем их в голубой цвет
    used_neighbors = set()  # Для исключения дублирования
    for i, r in obj_hex.iterrows():
        if r["object_count"] > 0:  # Только для гексов с объектами
            neighbors = h3.k_ring(r["h3_8"], k=1)  # Находим соседей
            print("r[h3_8] ", r["h3_8"],"neigbors ", neighbors)
            used_neighbors.add(r["h3_8"]) #Чтобы не закрашивались полигоны которые уже имеют объекты
            for neighbor in neighbors:
                if neighbor != r["h3_8"] and neighbor in olhon_hex.index:  # Сосед из olhon_hex
                    if neighbor not in used_neighbors:
                        neighbor_geom = Polygon(h3.h3_to_geo_boundary(neighbor, geo_json=True))
                        folium.GeoJson(
                            data=neighbor_geom.__geo_interface__,
                            style_function=lambda feature: {
                                "color": "blue",  # Голубой цвет для соседей
                                "weight": 1,
                                "fillOpacity": 0.3,
                            },
                        ).add_to(m)
                        used_neighbors.add(neighbor)

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
            # Сохраняем карту
    m.save("map.html")
    webbrowser.open("map.html")
        #print('i = ',i,' r = ',r["object_count"],' g = ',r["geometry"])


def markers_obj(map,df):
    # Вывод маркеров мест на карту
    for index, rows in df.iterrows():
        folium.Marker(
            location=[rows["lat"], rows["lng"]],
            tooltip="Click me!",
            popup=rows["name"],
            icon=folium.Icon(icon="place_icon.png"),
        ).add_to(map)
    return map

#IMPORTANT
# if __name__== '__main__':
#   markers_obj(m,df_cat_olkhon)
#   main(df_cat_olkhon)
#   webbrowser.open("map.html")
  
# создается dataFrame с типами и выборка значений по выбранному типу бизнеса
def filter_type(df, type_obj, type_business):
    df_type = pd.DataFrame({"type":type_obj}) 
    filtered_df = df_type[df_type['type'].apply(lambda x: type_business in x if isinstance(x, list) else x == type_business)]
    indexes = filtered_df.index #получение индексов заданных типов
    filter_df = df.loc[indexes] #поиск мест размещение с соответсвующим типу индексом
    main(filter_df)
    return filter_df
print(filter_type(df_cat_olkhon,type_cat_obj, type_business))