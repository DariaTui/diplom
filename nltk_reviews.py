# import nltk
# # nltk.download('punkt_tab')
# # nltk.download('stopwords')
# # nltk.download('omw-1.4')

import pymorphy2
import nltk
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import string
import pandas as pd
from connect_bd import connection



TABLES = {
    "catering": {"catering_olkhon"},
    "placement": {"placement_location_olkhon_test"},
    "catering_r": {"reviews_caterings"},
    "placement_r": {"reviews_pl_olkhon"}
}
id = {
    "catering": {"id_cat"},
    "placement": {"id_place"}
}
query_select_text_cat = "select id, text from reviews_caterings"

query_select_text_pl = "select id, text from reviews_pl_olkhon"
connection = connection
# Инициализация модуля pymorphy2
morph = pymorphy2.MorphAnalyzer()

# Списки позитивных и негативных слов (используем стемминг)
positive_words = {
    "чист", "вкусн", "невероятн", "свеж", "хорош", "отличн", "прекрасн", "лучш", "замечательн", "приятн",
    "добр", "качествен", "уютн", "тепл", "быстр", "радушн", "комфортн", "красив", "великолепн", "изыскан",
    "душевн", "вежлив", "внимательн", "аккуратн", "интересн", "весел", "дружелюбн", "положительн",
    "мил", "супер", "обалден", "гостеприимн", "ласков", "светл", "восхитительн", "идеальн", "фантастическ",
    "шикарн", "чудесн", "демократичн", "домашн", "настоящ", "сытн", "сыт", "лучший", "любимый",
    "бюджетн", "изумительн", "богат", "аппетитн", "замечателен", "профессиональн", "неповторим",
    "приятно", "уютно", "достойн", "восторг", "обслуживающ", "волшебн", "оригинальн", "сказочн", "разнообразн"
}


negative_words = {
    "плох", "грязн", "ужасн", "неприятн", "мерзк", "отвратительн", "скучн", "груб", "долг", "холодн",
    "разочарован", "дорог", "медленн", "неудобн", "громк", "надменн", "хамск", "разбит", "слом", "стар",
    "вонюч", "тесн", "посредствен", "уставш", "облезл", "уныл", "некрасив", "некачествен", "дешёв",
    "неудовлетворительн", "отстойн", "грязнул", "раздражающ", "нагл", "печальн", "ограничен",
    "непрофессиональн", "опасн", "обман", "вор", "развод", "нечестн", "невкусн", "антисанитар",
    "разбодяжен", "неадекватн", "неопытн", "безвкусн", "пересолен", "остывш", "грубый", "мутн",
    "тускл", "раздражающ", "неудовлетворен", "страшн", "нечист", "разваливающ", "жестк", "разбавлен"
}

#функция для обработки тональности отзывов 
def review_processin(review, negative_words,positive_words):
    # Загружаем стоп-слова и стеммер
    stop_words = set(stopwords.words("russian"))
    stemmer = SnowballStemmer("russian")

    # Токенизация
    words = word_tokenize(review)

    # Итоговые списки плюсов и минусов
    pros = []
    cons = []

    # Обработка текста
    processed_words = []
    i = 0  # Индекс для прохода по словам

    while i < len(words):
        word = words[i].lower().strip(string.punctuation)  # Приводим к нижнему регистру и убираем знаки препинания
        if word and word not in stop_words:  # Убираем стоп-слова и пустые строки
            stemmed_word = stemmer.stem(word)  # Применяем стемминг
            processed_words.append(stemmed_word)

            # Проверяем, является ли слово позитивным или негативным
            if stemmed_word in positive_words:
                
                phrase = word  # Запоминаем позитивное слово
                if morph.parse(word)[0].tag.POS=="ADJF":
                    if i + 1 < len(words):  # Проверяем, есть ли следующее слово
                        next_word = words[i + 1].strip(string.punctuation)
                        
                        if next_word and next_word not in stop_words and morph.parse(next_word)[0].tag.POS=="NOUN":  # Если следующее слово не знак препинания и следующее слово сущ
                            phrase += " " + next_word  # Добавляем его к плюсу
                            pros.append(phrase)
                elif morph.parse(word)[0].tag.POS=="ADVB":
                    pros.append(phrase)

            elif stemmed_word in negative_words:
                phrase = word  # Запоминаем негативное слово
                if morph.parse(word)[0].tag.POS=="ADJF":
                    if i + 1 < len(words):  # Проверяем, есть ли следующее слово
                        next_word = words[i + 1].strip(string.punctuation)
                        if next_word and next_word not in stop_words and morph.parse(next_word)[0].tag.POS=="NOUN":  # Если следующее слово не знак препинания
                            phrase += " " + next_word  # Добавляем его к минусу
                    cons.append(phrase)
                elif morph.parse(word)[0].tag.POS=="ADVB":
                    cons.append(phrase)
        
        i += 1  # Переход к следующему слову
    return pros, cons   
    
import pymysql
#функция преобразует в списки и добавляет плюсы и минусы в бд
def add_cons_pros(query_select_text, connection,table_review):
    pd_read_sql = pd.read_sql(query_select_text, connection)
    list_reviews = pd_read_sql.values.tolist()

    update_data = []  # Список для batch update

    for review in list_reviews:
        review_id = review[0]
        pros, cons = review_processin(review[1], negative_words, positive_words)

        # Преобразуем списки в строки для записи в MySQL
        pros_text = ", ".join(pros) if pros else None
        cons_text = ", ".join(cons) if cons else None

        update_data.append((pros_text, cons_text, review_id))

    # Обновляем БД
    update_query = "UPDATE {0} SET pros = %s, cons = %s WHERE id = %s".format(table_review)

    try:
        with connection.cursor() as cursor:
            cursor.executemany(update_query, update_data)
        connection.commit()
        print("Данные успешно обновлены в БД!")
    except pymysql.MySQLError as e:
        print(f"Ошибка при обновлении: {e}")
        connection.rollback()

#Занесение частовстречаемых pros cons из таблицы reviews_caterings в catering_olkhon.
import pymysql
import pandas as pd
from collections import Counter

def get_top_phrases(text_list, top_n=3, min_count=2):
    """
    Возвращает top_n наиболее часто встречающихся фраз (если нет повторений, берёт первые top_n).
    """
    phrases = [phrase.strip() for text in text_list if text for phrase in text.split(", ")]
    counter = Counter(phrases)
    # Выбираем только те фразы, которые встречаются минимум min_count раз
    frequent_phrases = [phrase for phrase, count in counter.most_common() if count >= min_count]

    # Если недостаточно частых фраз, дополняем их первыми 3 (чтобы не было пустых значений)
    if len(frequent_phrases) < top_n and len(phrases) > top_n:
        unique_phrases = list(dict.fromkeys(phrases))  # Сохраняем порядок
        frequent_phrases = (frequent_phrases + unique_phrases)[:top_n]

    return ", ".join(set(frequent_phrases[:top_n])) if frequent_phrases else None

def update_pros_cons(connection, table, table_r, id):
    """
    Выбирает часто встречающиеся pros и cons из reviews_caterings и обновляет catering_olkhon
    """
    try:
        with connection.cursor() as cursor:
            # Получаем все отзывы, сгруппированные по id_cat
            query = "SELECT {0}, pros, cons FROM {1} WHERE {0} IS NOT NULL".format(id,table_r)
            df = pd.read_sql(query, connection)

            # Группируем данные по id_cat
            grouped = df.groupby(id).agg(list)
            update_data = []  # Список для batch update

            for id, row in grouped.iterrows():
                common_pros = get_top_phrases(row["pros"])
                common_cons = get_top_phrases(row["cons"])
                print(common_cons)
            
                # Если есть что обновлять, добавляем в список
                if common_pros or common_cons:
                    update_data.append((common_pros if common_pros else None, 
                                        common_cons if common_cons else None, 
                                        id))

            # SQL-запрос на обновление catering_olkhon
            update_query = "UPDATE {0} SET pros = %s, cons = %s WHERE {1} = %s".format(table, id)

            # Выполняем batch update
            if update_data:
                cursor.executemany(update_query, update_data)
                connection.commit()
                print("Данные успешно обновлены в {0}!".format(table))
            else:
                print("Нет данных для обновления.")

    except pymysql.MySQLError as table:
        print(f"Ошибка при обновлении: {table}")
        connection.rollback()


# Запускаем обновление
add_cons_pros(query_select_text_pl, connection, list(TABLES["placement_r"])[0])
# Запуск обновления
update_pros_cons(connection, list(TABLES["placement"])[0], list(TABLES["placement_r"])[0], list(id["placement"])[0])

# Запускаем обновление
add_cons_pros(query_select_text_pl, connection, list(TABLES["catering_r"])[0])
# Запуск обновления
update_pros_cons(connection, list(TABLES["catering"])[0], list(TABLES["catering_r"])[0], list(id["catering"])[0])