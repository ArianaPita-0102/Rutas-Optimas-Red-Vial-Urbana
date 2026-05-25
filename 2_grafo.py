import pandas as pd
import networkx as nx
import pickle

nodos = pd.read_csv("nodes_limpio.csv")
aristas = pd.read_csv("edges_limpio.csv")

# grafo dirigido porque las calles tienen sentido
G = nx.DiGraph()

# agregamos nodos con sus coordenadas
for _, r in nodos.iterrows():
    G.add_node(r["node_id"], lat=r["lat"], lon=r["lon"])

# agregamos aristas con distancia y tiempo como pesos
for _, r in aristas.iterrows():
    G.add_edge(r["from_id"], r["to_id"],
               distancia=r["distance_m"],
               tiempo=r["tiempo_min"],
               fclass=r["fclass"])
    # si no es de un solo sentido, agregamos la vuelta
    if r["oneway"] == 0:
        G.add_edge(r["to_id"], r["from_id"],
                   distancia=r["distance_m"],
                   tiempo=r["tiempo_min"],
                   fclass=r["fclass"])

print(f"Grafo construido — nodos: {G.number_of_nodes()}, aristas: {G.number_of_edges()}")

# guardamos el grafo para no reconstruirlo en cada script
with open("grafo.pkl", "wb") as f:
    pickle.dump(G, f)

print("Grafo guardado en grafo.pkl")