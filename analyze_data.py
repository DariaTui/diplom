import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from connect_bd import connection  
import wordcloud

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
        print(df)
    except Exception as e:
        return (f"Ошибка загрузки данных из БД: {e}")

    if df.empty:
        return ("Нет данных для отображения облака слов.")
    
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd

def generate_wordcloud(category, phrase_type):
    table_name = "reviews_caterings" if category == "catering" else "reviews_pl_olkhon"

    try:
        query = f"SELECT {phrase_type} FROM {table_name} WHERE {phrase_type} IS NOT NULL"
        df = pd.read_sql(query, connection)
    except Exception as e:
        return f"Ошибка загрузки данных из БД: {e}"

    if df.empty:
        return "Нет данных для отображения облака слов."

    # Разделение фраз по запятым, очистка пробелов и создание общего текста
    all_phrases = df[phrase_type].dropna().astype(str)
    words = []

    for phrase in all_phrases:
        words.extend([word.strip() for word in phrase.split(',') if word.strip()])

    # Объединение слов в одну строку для wordcloud
    text = ' '.join(words)

    # Генерация облака слов
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path='arial', collocations=False).generate(text)

    # Отображение облака
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("Облако слов")
    plt.show()

generate_wordcloud("catering", "cons")