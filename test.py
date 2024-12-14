import osmnx as ox
import folium
import networkx as nx
import webbrowser
from polygonal_grid import df_olkhon, place, m 

ox.config(log_console=True, use_cache=True)
# define the start and end locations in latlng
start_latlng = (df_olkhon["lat"][0],df_olkhon["lng"][0])
end_latlng = (df_olkhon["lat"][1],df_olkhon["lng"][1])

# кратчайший маршрут в зависимости от способа передвижения
mode = "walk" # 'drive', 'bike', 'walk'

# найти кратчайший путь в зависимости от расстояния или времени
optimizer = 'length' # 'length','time'

# создать график из OSM в границах некоторого геокодируемого места
graph = ox.graph_from_place(place, network_type = mode)

# найти ближайший узел к начальной локации
orig_node = ox.nearest_nodes(graph, df_olkhon["lat"][0],df_olkhon["lng"][0])

# найти ближайший узел к конечной локации
dest_node  = ox.nearest_nodes(graph, df_olkhon["lat"][1],df_olkhon["lng"][1])

#нахождение крайчайшего расстояния
shortest_route = nx.shortest_path(graph, orig_node, dest_node, weight=optimizer)

#shortest_route_map=ox.graph_to_gdfs(graph,shortest_route)
#--Задачи--
#найти способ перевести данные shortest_route_map в geoJson
#почему при преобразовании список пуст ?
route_edges = list(zip(shortest_route[:-1], shortest_route[1:]))
nodes, edges = ox.graph_to_gdfs(graph)
edges_route = edges.loc[edges.index.isin(list(zip(shortest_route[:-1], shortest_route[1:])))]

print(edges_route)
# Добавление маршрута
folium.GeoJson(edges_route).add_to(m)

#folium.GeoJson(shortest_route_map).add_to(m)

m.save("test_map.html")
webbrowser.open("test_map.html")

