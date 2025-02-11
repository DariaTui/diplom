# import nltk
# # nltk.download('punkt_tab')
# # nltk.download('stopwords')
# # nltk.download('omw-1.4')

# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem.snowball import SnowballStemmer

# # Списки позитивных и негативных слов (используем стемминг)
# positive_words = {"чист", "вкусн", "невероятн", "свеж", "хорош", "отличн", "прекрасн", "лучш", "замечательн", "приятн"}
# negative_words = {"плох", "грязн", "ужасн", "неприятн", "мерзк", "отвратительн", "скучн", "груб", "долг", "холодн"}

# word_senteses = word_tokenize("Чистый. Удивительно вкусные позы и черебуки, невероятные! Все свежее, только что приготовленное. Спасибо! Плохой сервис, хороший ")
# stop_words = set(stopwords.words("russian"))
# stemmer = SnowballStemmer("russian")
# for i, w in enumerate(word_senteses):
#     if w in stop_words:
#         word_senteses.remove(w)
#     else:
#         word_senteses[i]=stemmer.stem(w)
# print(word_senteses)

# pros = []
# cons = []
import pymorphy2
import nltk
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import string
import pandas as pd
from connect_bd import connection

query_select_text = "select id, text from reviews_caterings"
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



#функция для заполнение cons pros
def add_cons_pros(query_select_text, connection):
    pd_read_sql = pd.read_sql(query_select_text, connection)
    list_reviews = pd_read_sql.values.tolist()
    for i in list_reviews:
        cons_pros = review_processin(i[1], negative_words,positive_words)
        print(cons_pros)
        
    
add_cons_pros(query_select_text, connection)    

import pymysql

def add_cons_pros(query_select_text, connection):
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
    update_query = """
        UPDATE reviews_caterings 
        SET pros = %s, cons = %s 
        WHERE id = %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.executemany(update_query, update_data)
        connection.commit()
        print("✅ Данные успешно обновлены в БД!")
    except pymysql.MySQLError as e:
        print(f"⚠️ Ошибка при обновлении: {e}")
        connection.rollback()

# Запускаем обновление
add_cons_pros(query_select_text, connection)



