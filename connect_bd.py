import pymysql 
import pandas as pd
import h3

def connect_with_bd():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            passwd="122002",
            database="tourism"
        )
        res_list=[]
        with connection:
            with connection.cursor() as cursor:
                z="SELECT name,lat,lon FROM sights_olkhon"
                cursor.execute(z)
                result = cursor.fetchall()

            #     for i in result:
            #         res_list.append(i)
            #         # print(i)
            #         # print("*"*20)
            # return print(res_list)   

    except Exception as ex:
        print("Connection refused...")
        print(ex)
        
connection = pymysql.connect(
            host="localhost",
            user="root",
            passwd="122002",
            database="tourism"
        )
query="SELECT name,latitude,longitude FROM sights_olkhon"
pd_data = pd.read_sql(query,connection)

df = pd_data[['name','latitude','longitude']]
#df = pd_data.rename(columns={"lat":"lat","lon":"lng"})
#lat_lng=df[['lat','lon']]
df_lat = df["latitude"].values.tolist()
df_lon = df["longitude"].values.tolist()
name_obj = df["name"].values.tolist()
