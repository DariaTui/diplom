import pymysql 
import pandas as pd
import h3

tables = ["sights_olkhon"]
req_unique_type = "select distinct type from {};".format(tables[0])

#выборка уникальных типов из бд
def separation_of_types(tables,req_unique_type):
    types_obj = set()
    pd_data_type = pd.read_sql(req_unique_type,connection)
    for index, row in pd_data_type.iterrows():
        for line in row:
            types_obj.update(line.split(','))
    types_obj = sorted(list(types_obj))
    return types_obj

def connect_with_bd(): 

    query="SELECT name,latitude,longitude FROM sights_olkhon"
    pd_data = pd.read_sql(query,connection)
    df = pd_data[['name','latitude','longitude']]

    df_lat = df["latitude"].values.tolist()
    df_lon = df["longitude"].values.tolist()
    name_obj = df["name"].values.tolist()
    print(df_lat)
    return df_lat, df_lon, name_obj
    

connection = pymysql.connect(
            host="localhost",
            user="root",
            passwd="122002",
            database="tourism"
        )
df_lat, df_lon, name_obj = connect_with_bd()
#print(separation_of_types(tables,req_unique_type))