import os
import webbrowser

def create_maps(name_map,m):
    if not os.path.exists("static"):
        os.makedirs("static")

    # Сохраняем карту
    file_path = os.path.join("static", name_map)
    m.save(file_path)
    return m
