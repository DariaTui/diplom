import folium
import json
import webbrowser
from polygonal_grid import markers_obj

# Путь к вашему файлу geojson
file_path = "datas/routes_Baikal.geojson"
file_path_OOP = "datas/OOPT_BP.geojson"
#файл для сохранения и вывода карты
file_name = "map_routes.html"
# Чтение GeoJSON
with open(file_path, 'r', encoding='utf-8') as file:
    geojson_data = json.load(file)

#file_OOP = 

# Создание базовой карты
m = folium.Map(location=[53.1036586, 107.3496115], zoom_start=9)

# Добавление GeoJSON-данных на карту
folium.GeoJson(geojson_data).add_to(m)

# Сохранение карты в файл и открытие в браузере
markers = markers_obj(m)
markers.save(file_name)
m.save(file_name)
print("Карта сохранена в map_routes.html. Откройте файл в браузере.")
webbrowser.open(file_name)
