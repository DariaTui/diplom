import numpy as np
import pandas as pd
    
data = np.array([17, 66, 3, 12, 6, 1, 7, 1, 3, 6, 2, 9, 1, 4, 1, 2, 1, 1, 4, 1, 3, 1, 8, 1, 3, 5, 2, 16, 8, 2, 1, 2, 1, 1, 1, 4, 1, 7, 2, 3, 1, 3, 1, 2, 1, 3, 1, 1, 2, 1, 1, 1, 1, 1, 31, 14, 5, 1, 9, 1, 15, 1, 1, 2, 4, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2])

def z_normalize_data(data, column_name=None):

    if column_name == "degree_landshaft_zone":
        result = np.zeros(len(data))
        result[data == 2] = 1
        result[data == 3] = 1
        return result
    else:
        mean = np.mean(data)  # Среднее значение
        std_dev = np.std(data)  # Стандартное отклонение

        if std_dev == 0:  # Защита от деления на 0
            return np.zeros(len(data))

        # Нормализация
        z_scores = (data - mean) / std_dev

        return z_scores  # Возвращаем нормализованные значения

def minmax_normalize_data(data, column_name=None):
    if column_name == "degree_landshaft_zone":
        result = np.zeros(len(data))
        result[data == 2] = 1
        result[data == 3] = 1
        return result
    elif column_name == "degree_favorability_z_score":
        mask_zeros = data == 0
        df_normalized = data.copy()
        X_std = (data - data.min()) / (data.max() - data.min())
        df_normalized = X_std * (1 - (0)) + (0)
        df_normalized[mask_zeros] = 0
        return df_normalized
    elif column_name == "distance_to_route":
        df_normalized = data.copy()
        X_std = (data - data.min()) / (data.max() - data.min())
        df_normalized = X_std * (1 - (0)) + (0)
        return df_normalized
    else:
    #if column_name != "degree_landshaft_zone" and column_name != 'degree_favorability':
        df_normalized = data.copy()
        X_std = (data - data.min()) / (data.max() - data.min())
        df_normalized = X_std * (1 - 0) + 0
        return df_normalized


def corr_data(data, column_name=None):
    return data.corr()

#метод оценки значимости рисков
def assessment_significance_risks(df1,df2):
    # Весовые коэффициенты для каждого критерия
    weights = {
        'competitor_density': 0.4,
        'tourist_route_proximity': 0.35,
        'landmark_proximity': 0.25
    }
    
    polygons_ratings = []
    
    for polygon in polygons_data:
        rating = (
            polygon['competitor_density'] * weights['competitor_density'] +
            polygon['tourist_route_proximity'] * weights['tourist_route_proximity'] +
            polygon['landmark_proximity'] * weights['landmark_proximity']
        )
        
        polygons_ratings.append({
            'polygon_id': polygon['id'],
            'rating': rating
        })
    
    return sorted(polygons_ratings, key=lambda x: x['rating'], reverse=True)


# Пример использования функции
polygons_data = [
    {'id': 1, 'competitor_density': 0.8, 'tourist_route_proximity': 0.6, 'landmark_proximity': 0.7},
    {'id': 2, 'competitor_density': 0.9, 'tourist_route_proximity': 0.4, 'landmark_proximity': 0.8},
    {'id': 3, 'competitor_density': 0.75, 'tourist_route_proximity': 0.65, 'landmark_proximity': 0.55}
]

