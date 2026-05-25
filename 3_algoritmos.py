import pickle
import networkx as nx

with open("grafo.pkl", "rb") as f:
    G = pickle.load(f)

print(f"Grafo cargado — nodos: {G.number_of_nodes()}, aristas: {G.number_of_edges()}\n")

# ── OBJETIVO 1: alcance vehicular ─────────────────────────────────────────────
# cuantos nodos son alcanzables desde un origen en max 5000 metros
origen = list(G.nodes())[0]
alcanzables = nx.single_source_dijkstra_path_length(G, origen, cutoff=5000, weight="distancia")
print(f"[1] Alcance vehicular desde nodo {origen}: {len(alcanzables)} nodos en <= 5 km")

# ── OBJETIVO 2: islas viales ──────────────────────────────────────────────────
# componentes debilmente conexas = grupos de calles desconectados entre si
componentes = list(nx.weakly_connected_components(G))
componentes.sort(key=len, reverse=True)
print(f"\n[2] Islas viales")
print(f"    Total de componentes: {len(componentes)}")
print(f"    Componente gigante:   {len(componentes[0])} nodos")
print(f"    Islas pequeñas:       {len(componentes) - 1}")

# ── OBJETIVO 3: diametro vial ─────────────────────────────────────────────────
# par de nodos con mayor distancia minima dentro de la componente gigante
# usamos una muestra porque el grafo completo es muy grande
G_gigante = G.subgraph(componentes[0]).copy()
muestra = list(G_gigante.nodes())[:500]  # 500 nodos representativos

max_dist = 0
par_max = (None, None)
for n in muestra:
    distancias = nx.single_source_dijkstra_path_length(G_gigante, n, weight="distancia")
    for destino, dist in distancias.items():
        if dist > max_dist:
            max_dist = dist
            par_max = (n, destino)

print(f"\n[3] Diametro vial (muestra 500 nodos)")
print(f"    Par mas distante: {par_max[0]} -> {par_max[1]}")
print(f"    Distancia: {max_dist/1000:.2f} km")

# ── OBJETIVO 4: red de emergencia minima (MST) ────────────────────────────────
# arbol que conecta todos los nodos con la menor distancia total posible
G_no_dirigido = G_gigante.to_undirected()
mst = nx.minimum_spanning_tree(G_no_dirigido, weight="distancia")
total_km = sum(d["distancia"] for _, _, d in mst.edges(data=True)) / 1000
print(f"\n[4] Red de emergencia minima (MST)")
print(f"    Nodos cubiertos: {mst.number_of_nodes()}")
print(f"    Aristas en MST:  {mst.number_of_edges()}")
print(f"    Distancia total: {total_km:.2f} km")