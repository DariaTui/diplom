from flask import Flask, render_template, request, jsonify
import folium
import os
import sys

# Добавляем пути к модулям
sys.path.append(r'C:\Users\User\Desktop\studyyy\diplom\coding\diplom')
from main import filter_type
from zoning_olkhon import zone_olkhon
from density_obj import density_map_function

app = Flask(__name__)

def create_map(business_type):

    map_object = filter_type(business=business_type)
    map_path = os.path.join('static', 'kbs_map.html')
    map_object.save(map_path)
    return map_path

def create_zone_map():
    map_object = zone_olkhon()
    map_path = os.path.join('static', 'zone_map.html')
    map_object.save(map_path)
    return map_path

def create_density_map(type_obj, type_business, price, rating, kitchen):
    map_object = density_map_function(type_obj=type_obj,type_business=type_business, price=price, rating=rating, kitchen=kitchen)
    map_path = os.path.join('static', f"{type_obj}_density.html")
    map_object.save(map_path)
    return map_path

@app.route('/')
def index():
    return render_template('index.html', map_file='kbs_map.html')

@app.route('/update_map', methods=['POST'])
def update_map():
    business_type = request.form['business']
    map_path = create_map(business_type)
    return jsonify({'map_file': map_path})

@app.route('/switch_map', methods=['POST'])
def switch_map():
    map_path = create_zone_map()
    return jsonify({'map_file': map_path})

@app.route('/density_map', methods=['POST']) 
def density_map():
    type_obj = request.form.get("type")
    
    if not type_obj:
        return jsonify({'error': 'Missing type parameter'}), 400

    # Получаем параметры, если они есть
    type_business = request.form.get("placeType")  # Для общепита
    price = request.form.get("price")
    rating = request.form.get("rating")
    kitchen = request.form.get("cuisine")  # Для общепита

    # Создаём карту
    map_path = create_density_map(type_obj, type_business, price, rating, kitchen)
    
    return jsonify({'map_file': map_path})

if __name__ == '__main__':
    app.run(debug=True)
