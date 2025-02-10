import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Путь к вашему файлу .tif
tif_file = 'path_to_your_file.tif'

# Ольхон и его границы
place = "остров Ольхон"
gdf = ox.geocode_to_gdf(place, which_result=1) 
# Создаем карту
m = folium.Map([gdf.centroid.y, gdf.centroid.x])

# Открываем файл с помощью rasterio
with rasterio.open(tif_file) as src:
    # Читаем данные
    data = src.read(1)  # Читаем первый канал (если изображение многоканальное, можно выбрать другой)
    
    # Получаем метаданные, включая координаты
    transform = src.transform
    extent = [transform[2], transform[2] + transform[0] * src.width,
              transform[5] + transform[4] * src.height, transform[5]]

    # Создаем карту с использованием cartopy
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Добавляем географические элементы на карту
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.OCEAN)
    
    # Отображаем изображение на карте
    img = ax.imshow(data, extent=extent, transform=ccrs.PlateCarree(), cmap='viridis')
    
    # Добавляем цветовую шкалу
    plt.colorbar(img, ax=ax, orientation='vertical', label='Значение пикселя')
    
    # Заголовок карты
    plt.title('Изображение на карте')
    
    # Показать карту
    plt.show()