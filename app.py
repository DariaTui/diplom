import dash
from dash import dcc, html, Input, Output, State
import folium
import os
import osmnx as ox
from map_create import create_maps
from main import filter_type
from zoning_olkhon import zone_olkhon
from density_obj import density_map_function
import plotly.graph_objs as go

#from analyze_data import get_phrases, create_wordcloud_figure

import pandas as pd
from connect_bd import connection

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

app = dash.Dash(__name__)
server = app.server  # для деплоя (если нужно)

STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

def create_map(business_type, weights):
    map_object = filter_type(business=business_type, weights=weights)
    map_path = os.path.join(STATIC_DIR, 'kbs_map.html')
    map_object.save(map_path)
    return map_path

def create_zone_map():
    map_object = zone_olkhon()
    map_path = os.path.join(STATIC_DIR, 'zone_map.html')
    map_object.save(map_path)
    return map_path

def create_density_map(type_obj, type_business, price, rating, kitchen):
    map_object = density_map_function(type_obj=type_obj, type_business=type_business,
                                      price=price, rating=rating, kitchen=kitchen)
    map_path = os.path.join(STATIC_DIR, f"{type_obj}_density.html")
    map_object.save(map_path)
    return map_path

def create_start_map(place="остров Ольхон"):
    gdf = ox.geocode_to_gdf(place, which_result=1)
    m = folium.Map([gdf.geometry.iloc[0].centroid.y, gdf.geometry.iloc[0].centroid.x], zoom_start=9)
    map_path = os.path.join(STATIC_DIR, "start_map.html")
    create_maps(map_path, m)
    return map_path

# Инициализируем стартовую карту
start_map = create_start_map()


#wordcloud
def generate_wordcloud(category, phrase_type):
    # Выбор таблицы
    table_name = "reviews_caterings" if category == "catering" else "reviews_pl_olkhon"

    # Подключение и загрузка данных
    try:
        query = f"SELECT {phrase_type} FROM {table_name} WHERE {phrase_type} IS NOT NULL"
        df = pd.read_sql(query, connection)
    except Exception as e:
        print(f"Ошибка при подключении или запросе: {e}")
        return html.Div("Ошибка загрузки данных")

    # Объединение всех фраз в один текст
    text_list = df[phrase_type].dropna().astype(str).tolist()
    full_text = " ".join(text_list).replace('.', '').replace(';', '')

    # Удаление пробелов, нормализация
    words = [word.strip().lower() for phrase in full_text.split(',') for word in phrase.split()]
    combined_text = " ".join(words)

    # Генерация облака слов
    wc = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(combined_text)

    # Сохранение в буфер
    buf = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    # Конвертация в base64
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    src = f'data:image/png;base64,{img_base64}'

    return html.Img(src=src, style={'width': '80%', 'height': 'auto'})

# --------- DASH UI ---------
app.layout = html.Div([
    html.H1("СППР для Ольхона", style={"textAlign": "center"}),

    html.Div([
        html.Label("Тип бизнеса:"),
        dcc.Dropdown(
            id='business-dropdown',
            options=[
                {'label': 'Общественное питание', 'value': 'public_eating'},
                {'label': 'Места размещения', 'value': 'accommodation_places'}
            ],
            value='public_eating'
        ),

        html.Label("Веса параметров:"),
        dcc.Input(id='weight1', type='number', value=1, placeholder='Вес 1'),
        dcc.Input(id='weight2', type='number', value=1, placeholder='Вес 2'),
        dcc.Input(id='weight3', type='number', value=1, placeholder='Вес 3'),
        dcc.Input(id='weight4', type='number', value=1, placeholder='Вес 4'),
        html.Button("Обновить карту", id='update-map', n_clicks=0),
        html.Button("Показать зонирование", id='zone-map', n_clicks=0),
    ], style={"margin": "20px"}),

    html.Iframe(
        id='map-frame',
        srcDoc=open(start_map, 'r', encoding='utf-8').read(),
        width='100%',
        height='600'
    ),

    html.H1("Облако слов отзывов", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Категория:"),
        dcc.Dropdown(
            id='category-dropdown',
            options=[
                {'label': 'Общественное питание', 'value': 'catering'},
                {'label': 'Размещение', 'value': 'placement'}
            ],
            value='catering',
            style={'width': '250px'}
        )
    ], style={'padding': '10px'}),

    html.Div([
        html.Label("Тип фраз:"),
        dcc.RadioItems(
            id='phrase-type',
            options=[
                {'label': 'Положительные (pros)', 'value': 'pros'},
                {'label': 'Негативные (cons)', 'value': 'cons'}
            ],
            value='pros',
            labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        )
    ], style={'padding': '10px'}),

    html.Div(id='wordcloud-graph', style={'textAlign': 'center', 'padding': '20px'})

])

# --------- CALLBACKS ---------

@app.callback(
    Output('map-frame', 'srcDoc'),
    Input('update-map', 'n_clicks'),
    Input('zone-map', 'n_clicks'),
    State('business-dropdown', 'value'),
    State('weight1', 'value'),
    State('weight2', 'value'),
    State('weight3', 'value'),
    State('weight4', 'value'),
    prevent_initial_call=True
)


def handle_map_buttons(update_clicks, zone_clicks, business, w1, w2, w3, w4):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'update-map':
        weights = {
            "other_object_count_score": w1,
            "distance_to_route_score": w2,
            "landmark_count_score": w3,
            "object_count_score": w4
        }
        file_path = create_map(business, weights)

    elif triggered_id == 'zone-map':
        file_path = create_zone_map()

    else:
        raise dash.exceptions.PreventUpdate

    return open(file_path, 'r', encoding='utf-8').read()

#облако слов
# @app.callback(
#     Output('wordcloud-graph', 'children'),
#     Input('category-dropdown', 'value'),
#     Input('phrase-type', 'value')
# )


def update_wordcloud(category, phrase_type):
    return generate_wordcloud(category, phrase_type)


# --------- RUN APP ---------
if __name__ == '__main__':
    app.run(debug=True)
