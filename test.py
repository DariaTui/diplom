import pandas as pd
import h3


# Пример DataFrame с данными
df_olkhon = pd.DataFrame({
    "name": ["Заслонка", "Скала Саган-Заба", "Мишкина гора"], 
    "lat": [52.60186, 52.67825, 52.54578], 
    "lng": [105.75050, 106.46595, 106.03729]
})

# Преобразуем координаты в H3
df_olkhon["h3_8"] = df_olkhon.apply(lambda row: h3.geo_to_h3(row["lat"], row["lng"], 8), axis=1)

# Подсчитаем количество объектов в каждом H3-гексагоне
df_olkhon['object_count'] = df_olkhon.groupby('h3_8')['name'].transform('count')

# Проверим результат
print(df_olkhon)
