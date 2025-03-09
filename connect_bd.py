import pymysql 
import pandas as pd
import h3

tables = ["sights_olkhon","catering_olkhon"]
req_unique_type = "select distinct type from {};".format(tables[0])
type_selection = ""

#перевод слов из бд
keywords_sights = {
    "музей": "museums",
    "смотровая площадка": "observation_deck",
    "сапсёрфинг": "sapsurfing"
}

keywords_caterings = {
    "Кафе": "cafe",
    "Ресторан": "restaurant",
    "Кофейня": "coffee_house",
    "Доставка еды и обедов": "delivery",
    "Пиццерия": "pizzeria",
    "Бар": "bar",
    "Паб": "pub",
    "Кальян-бар": "bar",
    "Мороженое": "ice-cream",
    "Турбаза": "hotel",
    "Гостиница": "hotel",
}

#выборка уникальных типов из бд
def separation_of_types(tables,req_unique_type):
    types_obj = set()
    pd_data_type = pd.read_sql(req_unique_type,connection)
    for index, row in pd_data_type.iterrows():
        for line in row:
            types_obj.update(line.split(','))
    types_obj = sorted(list(types_obj))
    return types_obj

# редактирование типов мест из бд
def splitting_types(df,keywords):
    type_obj = df["type"].values.tolist()
    for id_i, i in enumerate(type_obj):  # Используем enumerate для получения индекса
        if "," in i:
            type_obj[id_i] = i.split(sep=",")  # Изменяем элемент списка по индексу
        # изменение названий на англ для достопримечательностей
        for key, value in keywords.items():
            if key in i.lower():
                type_obj[id_i] = value
                break
            
    return type_obj

#функция по выбору общепитов из бд
def select_caterings():

    query="SELECT * FROM catering_olkhon"
    pd_cat_data = pd.read_sql(query,connection)
    df_cat = pd_cat_data[['id','name','latitude','longitude','type','pros','cons']]

    df_cat_id = df_cat["id"].values.tolist()
    df_cat_lat = df_cat["latitude"].values.tolist()
    df_cat_lon = df_cat["longitude"].values.tolist()
    name_cat_obj = df_cat["name"].values.tolist()
    df_cat_pros = df_cat["pros"].values.tolist()
    df_cat_cons = df_cat["cons"].values.tolist()
    type_cat_obj = splitting_types(df_cat,keywords_caterings)
    return df_cat_id, df_cat_lat, df_cat_lon, name_cat_obj, type_cat_obj, df_cat_pros, df_cat_cons

#функция по выбору общепитов из бд
def select_pl():

    query="SELECT * FROM placement_location_olkhon_test"
    pd_pl_data = pd.read_sql(query,connection)
    df_pl = pd_pl_data[['id','name','lat','lon','pros','cons']]

    df_pl_id = df_pl["id"].values.tolist()
    df_pl_lat = df_pl["lat"].values.tolist()
    df_pl_lon = df_pl["lon"].values.tolist()
    name_pl_obj = df_pl["name"].values.tolist()
    df_pl_pros = df_pl["pros"].values.tolist()
    df_pl_cons = df_pl["cons"].values.tolist()

    return df_pl_id, df_pl_lat, df_pl_lon, name_pl_obj,df_pl_pros, df_pl_cons

#функция по выбору достопримечательностей из бд
def select_sights(): 

    query="SELECT * FROM sights_olkhon"
    pd_data = pd.read_sql(query,connection)
    df = pd_data[["id",'name','latitude','longitude','type']]

    df_id = df["id"].values.tolist()
    df_lat = df["latitude"].values.tolist()
    df_lon = df["longitude"].values.tolist()
    name_obj = df["name"].values.tolist()
    #type_obj = df["type"].values.tolist()
    type_obj = splitting_types(df, keywords_sights)
    return df_id, df_lat, df_lon, name_obj, type_obj



connection = pymysql.connect(
            host="localhost",
            user="root",
            passwd="122002",
            database="tourism"
        )

df_id, df_lat, df_lon, name_obj, type_obj = select_sights()

df_cat_id, df_cat_lat, df_cat_lon, name_cat_obj, type_cat_obj, df_cat_pros, df_cat_cons = select_caterings()

df_pl_id, df_pl_lat, df_pl_lon, name_pl_obj,df_pl_pros, df_pl_cons = select_pl()

#print(df_pl_id)