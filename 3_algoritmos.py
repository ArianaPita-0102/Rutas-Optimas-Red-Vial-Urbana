import pandas as pd
import heapq
import time
from collections import defaultdict

# ── cargar grafo ──────────────────────────────────────────────────────────────
aristas = pd.read_csv("edges_limpio.csv")

adj_dist = defaultdict(list)
adj_time = defaultdict(list)
aristas_lista = []
todos_nodos = set()

for _, r in aristas.iterrows():
    u, v = int(r["from_id"]), int(r["to_id"])
    d, t = r["distance_m"], r["tiempo_min"]

    adj_dist[u].append((d, v))
    adj_time[u].append((t, v))
    aristas_lista.append((d, u, v))
    todos_nodos.add(u)
    todos_nodos.add(v)

    if r["oneway"] == 0:
        adj_dist[v].append((d, u))
        adj_time[v].append((t, u))
        aristas_lista.append((d, v, u))

print(f"Grafo cargado — nodos: {len(todos_nodos)}, aristas: {len(aristas)}\n")

# ── UNION FIND ────────────────────────────────────────────────────────────────
parent = {}
rank = {}

def init_uf(nodos):
    for n in nodos:
        parent[n] = n
        rank[n] = 0

def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(x, y):
    px, py = find(x), find(y)
    if px == py:
        return False
    if rank[px] < rank[py]:
        px, py = py, px
    parent[py] = px
    if rank[px] == rank[py]:
        rank[px] += 1
    return True

# ── DIJKSTRA con min-heap ─────────────────────────────────────────────────────
def dijkstra(adj, origen, limite=None):
    dist = defaultdict(lambda: float('inf'))
    dist[origen] = 0
    pq = [(0, origen)]

    while pq:
        d = pq[0][0]
        u = pq[0][1]
        heapq.heappop(pq)

        if d > dist[u]:
            continue

        for i in range(len(adj[u])):
            peso = adj[u][i][0]
            v    = adj[u][i][1]

            if limite is not None and dist[u] + peso > limite:
                continue

            if dist[u] + peso < dist[v]:
                dist[v] = dist[u] + peso
                heapq.heappush(pq, (dist[v], v))

    return dist

# ── OBJETIVO 1: alcance vehicular ─────────────────────────────────────────────
origen = list(todos_nodos)[0]
t0 = time.time()
dist = dijkstra(adj_dist, origen, limite=5000)
alcanzables = [v for v in dist if dist[v] <= 5000]
t1 = time.time()
print(f"[1] Alcance vehicular desde nodo {origen}")
print(f"    Nodos alcanzables en <= 5 km: {len(alcanzables)}")
print(f"    Tiempo de ejecucion: {t1-t0:.4f} segundos\n")

# ── OBJETIVO 2: islas viales con Union-Find ───────────────────────────────────
init_uf(todos_nodos)
t0 = time.time()
for i in range(len(aristas_lista)):
    _, u, v = aristas_lista[i]
    union(u, v)

grupos = defaultdict(list)
for n in todos_nodos:
    grupos[find(n)].append(n)

componentes = sorted(grupos.values(), key=len, reverse=True)
t1 = time.time()
print(f"[2] Islas viales")
print(f"    Total de componentes:  {len(componentes)}")
print(f"    Componente gigante:    {len(componentes[0])} nodos")
print(f"    Islas pequeñas:        {len(componentes) - 1}")
print(f"    Tiempo de ejecucion:   {t1-t0:.4f} segundos\n")

# ── OBJETIVO 3: diametro vial ─────────────────────────────────────────────────
gigante = set(componentes[0])
adj_gigante_dist = defaultdict(list)
adj_gigante_time = defaultdict(list)

for u in gigante:
    for i in range(len(adj_dist[u])):
        v = adj_dist[u][i][1]
        if v in gigante:
            adj_gigante_dist[u].append(adj_dist[u][i])

for u in gigante:
    for i in range(len(adj_time[u])):
        v = adj_time[u][i][1]
        if v in gigante:
            adj_gigante_time[u].append(adj_time[u][i])

muestra = list(gigante)[:500]
t0 = time.time()
max_dist = 0
par_max = (None, None)
for n in muestra:
    d = dijkstra(adj_gigante_dist, n)
    for v in d:
        if d[v] != float('inf') and d[v] > max_dist:
            max_dist = d[v]
            par_max = (n, v)
t1 = time.time()
print(f"[3] Diametro vial (muestra 500 nodos)")
print(f"    Par mas distante: {par_max[0]} -> {par_max[1]}")
print(f"    Distancia: {max_dist/1000:.2f} km")
print(f"    Tiempo de ejecucion: {t1-t0:.4f} segundos\n")

# ── OBJETIVO 4: kruskal con Union-Find ───────────────────────────────────────
init_uf(gigante)
aristas_gigante = [(d, u, v) for d, u, v in aristas_lista if u in gigante and v in gigante]
aristas_gigante.sort()

t0 = time.time()
mst_total = 0
mst_aristas = 0
for i in range(len(aristas_gigante)):
    d, u, v = aristas_gigante[i]
    if union(u, v):
        mst_total += d
        mst_aristas += 1
t1 = time.time()
print(f"[4] Red de emergencia minima (Kruskal + Union-Find)")
print(f"    Nodos cubiertos:     {len(gigante)}")
print(f"    Aristas en MST:      {mst_aristas}")
print(f"    Distancia total:     {mst_total/1000:.2f} km")
print(f"    Tiempo de ejecucion: {t1-t0:.4f} segundos\n")

# ── BONUS: distancia vs tiempo ────────────────────────────────────────────────
nodo_a = par_max[0]
nodo_b = par_max[1]

t0 = time.time()
dist_d = dijkstra(adj_gigante_dist, nodo_a)
t1 = time.time()

t2 = time.time()
dist_t = dijkstra(adj_gigante_time, nodo_a)
t3 = time.time()

print(f"[BONUS] Distancia vs Tiempo — nodos {nodo_a} -> {nodo_b}")
print(f"    Ruta optima por DISTANCIA:")
print(f"      Distancia:       {dist_d[nodo_b]/1000:.2f} km")
print(f"      Tiempo calculo:  {t1-t0:.4f} seg")
print(f"    Ruta optima por TIEMPO:")
print(f"      Tiempo estimado: {dist_t[nodo_b]:.2f} min")
print(f"      Tiempo calculo:  {t3-t2:.4f} seg")