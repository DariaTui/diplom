import nltk
# nltk.download('punkt_tab')
# nltk.download('stopwords')
# nltk.download('omw-1.4')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer

senteses = word_tokenize("Чисто. Удивительно вкусные позы и черебуки, невероятные! Все свежее, только что приготовленное. Спасибо! Плохой сервис, хороший ")
stop_words = set(stopwords.words("russian"))
stemmer = SnowballStemmer("russian")
for i, w in enumerate(senteses):
    if w in stop_words:
        senteses.remove(w)
    else:
        senteses[i]=stemmer.stem(w)
print(senteses)


# import pymysql 
# import pandas as pd
# tables = ["sights_olkhon","catering_olkhon"]