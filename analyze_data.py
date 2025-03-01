import numpy as np
    
data = np.array([70, 80, 90, 100, 110])

def normalize_data(data):
    mean = np.mean(data)  # Среднее значение
    std_dev = np.std(data)  # Стандартное отклонение

    if std_dev == 0:  # Защита от деления на 0
        return np.zeros(len(data))

    # Нормализация
    z_scores = (data - mean) / std_dev

    return z_scores  # Возвращаем нормализованные значения
print(normalize_data(data))