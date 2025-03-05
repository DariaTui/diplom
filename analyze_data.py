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
#print(normalize_data(data))

def minmax_normalize_data(X):
    X_std = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
    X_scaled = X_std * (1 - (-1)) + (-1)
    return X_scaled

def corr_data(data1, column_name=None):

    return data1.corr()