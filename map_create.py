import os
import webbrowser

def create_maps(name_map,m):
    # Проверяем папку "maps" и создаем её, если её нет
    if not os.path.exists("static"):
        os.makedirs("static")

    # Сохраняем карту
    file_path = os.path.join("static", name_map)
    m.save(file_path)
    return m
    # Открываем карту через абсолютный путь
    #webbrowser.open(f"file://{os.path.abspath(file_path)}")