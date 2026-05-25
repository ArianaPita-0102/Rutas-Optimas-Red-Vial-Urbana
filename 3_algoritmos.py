import pickle
import networkx as nx
import time

with open("grafo.pkl", "rb") as f:
    G = pickle.load(f)

print(f"Grafo cargado — nodos: {G.number_of_nodes()}, aristas: {G.number_of_edges()}\n")

# ── OBJETIVO 1: alcance vehicular ─────────────────────────────────────────────
t0 = time.time()
origen = list(G.nodes())[0]
alcanzables = nx.single_source_dijkstra_path_length(G, origen, cutoff=5000, weight="distancia")
t1 = time.time()
print(f"[1] Alcance vehicular desde nodo {origen}")
print(f"    Nodos alcanzables en <= 5 km: {len(alcanzables)}")
print(f"    Tiempo de ejecucion: {t1-t0:.4f} segundos\n")

# ── OBJETIVO 2: islas viales ──────────────────────────────────────────────────
t0 = time.time()
componentes = sorted(nx.weakly_connected_components(G), key=len, reverse=True)
t1 = time.time()
print(f"[2] Islas viales")
print(f"    Total de componentes:  {len(componentes)}")
print(f"    Componente gigante:    {len(componentes[0])} nodos")
print(f"    Islas pequeñas:        {len(componentes) - 1}")
print(f"    Tiempo de ejecucion:   {t1-t0:.4f} segundos\n")

# ── OBJETIVO 3: diametro vial ─────────────────────────────────────────────────
G_gigante = G.subgraph(componentes[0]).copy()
muestra = list(G_gigante.nodes())[:500]

t0 = time.time()
max_dist = 0
par_max = (None, None)
for n in muestra:
    distancias = nx.single_source_dijkstra_path_length(G_gigante, n, weight="distancia")
    for destino, dist in distancias.items():
        if dist > max_dist:
            max_dist = dist
            par_max = (n, destino)
t1 = time.time()
print(f"[3] Diametro vial (muestra 500 nodos)")
print(f"    Par mas distante: {par_max[0]} -> {par_max[1]}")
print(f"    Distancia: {max_dist/1000:.2f} km")
print(f"    Tiempo de ejecucion: {t1-t0:.4f} segundos\n")

# ── OBJETIVO 4: MST ───────────────────────────────────────────────────────────
t0 = time.time()
G_no_dirigido = G_gigante.to_undirected()
mst = nx.minimum_spanning_tree(G_no_dirigido, weight="distancia")
total_km = sum(d["distancia"] for _, _, d in mst.edges(data=True)) / 1000
t1 = time.time()
print(f"[4] Red de emergencia minima (MST)")
print(f"    Nodos cubiertos:     {mst.number_of_nodes()}")
print(f"    Aristas en MST:      {mst.number_of_edges()}")
print(f"    Distancia total:     {total_km:.2f} km")
print(f"    Tiempo de ejecucion: {t1-t0:.4f} segundos\n")

# ── BONUS: distancia vs tiempo entre mismo par ────────────────────────────────
nodo_a = par_max[0]
nodo_b = par_max[1]

t0 = time.time()
camino_dist = nx.dijkstra_path(G_gigante, nodo_a, nodo_b, weight="distancia")
dist_ruta = nx.dijkstra_path_length(G_gigante, nodo_a, nodo_b, weight="distancia")
t1 = time.time()
tiempo_ruta_dist = sum(G_gigante[u][v]["tiempo"] for u, v in zip(camino_dist[:-1], camino_dist[1:]))

t2 = time.time()
camino_tiempo = nx.dijkstra_path(G_gigante, nodo_a, nodo_b, weight="tiempo")
dist_tiempo = nx.dijkstra_path_length(G_gigante, nodo_a, nodo_b, weight="tiempo")
t3 = time.time()
distancia_ruta_tiempo = sum(G_gigante[u][v]["distancia"] for u, v in zip(camino_tiempo[:-1], camino_tiempo[1:]))

print(f"[BONUS] Comparacion distancia vs tiempo — nodos {nodo_a} -> {nodo_b}")
print(f"    Ruta optima por DISTANCIA:")
print(f"      Distancia:       {dist_ruta/1000:.2f} km")
print(f"      Tiempo estimado: {tiempo_ruta_dist:.2f} min")
print(f"      Nodos en ruta:   {len(camino_dist)}")
print(f"      Tiempo calculo:  {t1-t0:.4f} seg")
print(f"    Ruta optima por TIEMPO:")
print(f"      Distancia:       {distancia_ruta_tiempo/1000:.2f} km")
print(f"      Tiempo estimado: {dist_tiempo:.2f} min")
print(f"      Nodos en ruta:   {len(camino_tiempo)}")
print(f"      Tiempo calculo:  {t3-t2:.4f} seg")