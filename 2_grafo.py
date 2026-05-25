import pandas as pd
import networkx as nx
import pickle

nodos = pd.read_csv("nodes.csv")
aristas = pd.read_csv("edges_limpio.csv")

G = nx.DiGraph()

for _, r in nodos.iterrows():
    G.add_node(r["node_id"], lat=r["lat"], lon=r["lon"])

for _, r in aristas.iterrows():
    G.add_edge(r["from_id"], r["to_id"],
               distancia=r["distance_m"],
               tiempo=r["tiempo_min"],
               fclass=r["fclass"])
    if r["oneway"] == 0:
        G.add_edge(r["to_id"], r["from_id"],
                   distancia=r["distance_m"],
                   tiempo=r["tiempo_min"],
                   fclass=r["fclass"])

print(f"Grafo construido — nodos: {G.number_of_nodes()}, aristas: {G.number_of_edges()}")

with open("grafo.pkl", "wb") as f:
    pickle.dump(G, f)

print("Grafo guardado en grafo.pkl")