import pymysql 
import pandas as pd
import h3

tables = ["sights_olkhon"]
req_unique_type = "select distinct type from {};".format(tables[0])
type_selection = ""

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
def splitting_types(df):
    type_obj = df["type"].values.tolist()
    for id_i, i in enumerate(type_obj):  # Используем enumerate для получения индекса
        if "," in i:
            type_obj[id_i] = i.split(sep=",")  # Изменяем элемент списка по индексу
        # изменение названий на англ
        if "музей" in i.lower():
            type_obj[id_i] = "museums"
        if "смотровая площадка" in i.lower():
            type_obj[id_i] = "observation_deck"
        if "сапсёрфинг" in i.lower():
            type_obj[id_i] = "sapsurfing"
            
    return type_obj

def connect_with_bd(): 

    query="SELECT name,latitude,longitude, type FROM sights_olkhon"
    pd_data = pd.read_sql(query,connection)
    df = pd_data[['name','latitude','longitude','type']]

    df_lat = df["latitude"].values.tolist()
    df_lon = df["longitude"].values.tolist()
    name_obj = df["name"].values.tolist()
    #type_obj = df["type"].values.tolist()
    type_obj = splitting_types(df)
    return df_lat, df_lon, name_obj, type_obj

connection = pymysql.connect(
            host="localhost",
            user="root",
            passwd="122002",
            database="tourism"
        )
df_lat, df_lon, name_obj, type_obj = connect_with_bd()
#print(df_lat, df_lon, name_obj, type_obj)
