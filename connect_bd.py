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
def splitting_types(df, keywords):
    type_obj = df["type"].values.tolist()
    for id_i, i in enumerate(type_obj):  # Используем enumerate для получения индекса
        if "," in i:
            type_obj[id_i] = ",".join(word.strip() for word in i.split(","))  # Убираем пробелы и соединяем обратно через запятую
        else:
            type_obj[id_i] = i.strip()  # Убираем пробелы из одиночных значений
    return type_obj

def clean_kitchen_column(df):
    kitchen_obj = df["kitchen"].values.tolist()
    for id_i, i in enumerate(kitchen_obj):
        if isinstance(i, str) and "," in i:
            kitchen_obj[id_i] = ",".join(word.strip() for word in i.split(","))  # Убираем пробелы и соединяем обратно через запятую
        elif isinstance(i, str):
            kitchen_obj[id_i] = i.strip()  # Убираем пробелы из одиночных значений
    return kitchen_obj

def select_caterings():
    query = "SELECT * FROM catering_olkhon"
    pd_cat_data = pd.read_sql(query, connection)
    df_cat = pd_cat_data[['id', 'name', 'latitude', 'longitude', 'type', 'pros', 'cons', 'midprice', 'kitchen', 'rating']]

    df_cat_id = df_cat["id"].values.tolist()
    df_cat_lat = df_cat["latitude"].values.tolist()
    df_cat_lon = df_cat["longitude"].values.tolist()
    name_cat_obj = df_cat["name"].values.tolist()
    df_cat_pros = df_cat["pros"].values.tolist()
    df_cat_cons = df_cat["cons"].values.tolist()

    type_cat_obj = splitting_types(df_cat, keywords_caterings)
    df_cat_kitchen = clean_kitchen_column(df_cat)

    df_cat_midprice = df_cat["midprice"].values.tolist()
    df_cat_rating = df_cat["rating"].values.tolist()

    return df_cat_id, df_cat_lat, df_cat_lon, name_cat_obj, type_cat_obj, df_cat_pros, df_cat_cons, df_cat_midprice, df_cat_kitchen, df_cat_rating

#функция по выбору общепитов из бд
def select_pl():

    query="SELECT * FROM placement_location_olkhon_test"
    pd_pl_data = pd.read_sql(query,connection)
    df_pl = pd_pl_data[['id','name','lat','lon','pros','cons', 'min_price', 'rating_total']]

    df_pl_id = df_pl["id"].values.tolist()
    df_pl_lat = df_pl["lat"].values.tolist()
    df_pl_lon = df_pl["lon"].values.tolist()
    name_pl_obj = df_pl["name"].values.tolist()
    df_pl_pros = df_pl["pros"].values.tolist()
    df_pl_cons = df_pl["cons"].values.tolist()

    df_pl_minprice = df_pl["min_price"].values.tolist()
    df_pl_rating = df_pl["rating_total"].values.tolist()

    return df_pl_id, df_pl_lat, df_pl_lon, name_pl_obj,df_pl_pros, df_pl_cons, df_pl_minprice, df_pl_rating

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

def filter_olkhon(df):
    # Границы острова Ольхон
    min_lat, max_lat = 53.05, 53.42
    min_lng, max_lng = 106.97, 108.76
    
    # Фильтрация DataFrame
    df_filtered = df[(df['lat'].between(min_lat, max_lat)) & (df['lng'].between(min_lng, max_lng))]
    return df_filtered

def choose_obj(type_obj):
    if type_obj == "public_eating":
        df = pd.DataFrame({
            "id": df_cat_id, "lat": df_cat_lat, "lng": df_cat_lon, "name": name_cat_obj,
            "pros": df_cat_pros, "cons": df_cat_cons, "price": df_cat_midprice,
            "rating": df_cat_rating, "kitchen": df_cat_kitchen, "type_business": type_cat_obj
        })
    elif type_obj == "accommodation_places":
        df = pd.DataFrame({
            "id": df_pl_id, "lat": df_pl_lat, "lng": df_pl_lon, "name": name_pl_obj,
            "pros": df_pl_pros, "cons": df_pl_cons, "price": df_pl_minprice, "rating": df_pl_rating
        })
    elif type_obj == "landmarks":
        df = pd.DataFrame({"id": df_id, "lat": df_lat, "lng": df_lon, "name": name_obj})
    else:
        return None
    
    # Фильтруем по границам Ольхонского района
    return filter_olkhon(df)

def select_pl_services():
    query="select * from service_pl_olkhon;"
    pd_data = pd.read_sql(query,connection)
    df = pd_data[["id",'type','category','isFree']]

    df_id = df["id"].values.tolist()
    df_type = df["type"].values.tolist()
    df_category = df["category"].values.tolist()
    df_isFree = df["isFree"].values.tolist()

    return df_id, df_type, df_category, df_isFree

df_id, df_lat, df_lon, name_obj, type_obj = select_sights()

df_cat_id, df_cat_lat, df_cat_lon, name_cat_obj, type_cat_obj, df_cat_pros, df_cat_cons, df_cat_midprice, df_cat_kitchen, df_cat_rating = select_caterings()

df_pl_id, df_pl_lat, df_pl_lon, name_pl_obj,df_pl_pros, df_pl_cons, df_pl_minprice, df_pl_rating = select_pl()

