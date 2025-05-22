import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from connect_bd import connection  
import os
from wordcloud import WordCloud

def minmax_normalize_data(data, column_name=None):
    if column_name == "degree_landshaft_zone":
        result = np.zeros(len(data))
        result[data == 2] = 1
        result[data == 3] = 1
        return result
    elif column_name == "degree_favorability_score":
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
        df_normalized = data.copy()
        X_std = (data - data.min()) / (data.max() - data.min())
        df_normalized = X_std * (1 - 0) + 0
        return df_normalized


def corr_data(data, column_name=None):
    return data.corr()

def generate_wordcloud(category, phrase_type):
    table_name = "reviews_caterings" if category == "catering" else "reviews_pl_olkhon"

    try:
        query = f"SELECT {phrase_type} FROM {table_name} WHERE {phrase_type} IS NOT NULL"
        df = pd.read_sql(query, connection)
    except Exception as e:
        return f"Ошибка загрузки данных из БД: {e}"

    if df.empty:
        return "Нет данных для отображения облака слов."

    # Обработка текста
    all_phrases = df[phrase_type].dropna().astype(str)
    words = []

    for phrase in all_phrases:
        parts = phrase.split(',')
        cleaned = [p.strip() for p in parts if p.strip()]
        words.extend(cleaned)

    text = ' '.join(words)

    # Генерация облака слов
    wordcloud = WordCloud(
        width=800, height=400, background_color='white',
        font_path='arial', collocations=False
    ).generate(text)

    # Путь для сохранения картинки
    output_path = os.path.join('static', 'wordcloud.png')
    os.makedirs('static', exist_ok=True) 

    wordcloud.to_file(output_path)

    return output_path