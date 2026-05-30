import time
from collections import defaultdict
from algoritmos import RedVial, UnionFind, Dijkstra, Kruskal

red_vial = RedVial()
red_vial.cargar_nodos("nodes.csv")
red_vial.cargar_aristas("edges_limpio.csv")

nodo_origen = list(red_vial.todos_nodos)[0]

tiempo_inicio = time.time()

algoritmo_dijkstra = Dijkstra(red_vial.adj_dist)
distancias = algoritmo_dijkstra.ejecutar(nodo_origen, limite=5000)

nodos_alcanzables = [
    nodo for nodo in distancias
    if distancias[nodo] <= 5000
]

tiempo_fin = time.time()

print(f"[1] Alcance vehicular desde nodo {nodo_origen}")

if nodo_origen in red_vial.nodos_coords:
    print(f"    Coordenadas origen: {red_vial.nodos_coords[nodo_origen]}")

print(f"    Nodos alcanzables en <= 5 km: {len(nodos_alcanzables)}")
print(f"    Tiempo de ejecucion: {tiempo_fin - tiempo_inicio:.4f} segundos\n")

tiempo_inicio = time.time()

estructura_union_find = UnionFind(red_vial.todos_nodos)

for indice in range(len(red_vial.aristas_lista)):
    _, nodo_a, nodo_b = red_vial.aristas_lista[indice]
    estructura_union_find.union(nodo_a, nodo_b)

componentes_por_representante = defaultdict(list)

for nodo in red_vial.todos_nodos:
    representante = estructura_union_find.find(nodo)
    componentes_por_representante[representante].append(nodo)

componentes_conectadas = sorted(
    componentes_por_representante.values(),
    key=len,
    reverse=True
)

tiempo_fin = time.time()

print(f"[2] Islas viales")
print(f"    Total de componentes:  {len(componentes_conectadas)}")
print(f"    Componente gigante:    {len(componentes_conectadas[0])} nodos")
print(f"    Islas pequeñas:        {len(componentes_conectadas) - 1}")
print(f"    Tiempo de ejecucion:   {tiempo_fin - tiempo_inicio:.4f} segundos\n")

componente_gigante = set(componentes_conectadas[0])

adyacencias_distancia_gigante = defaultdict(list)

for nodo_origen_gigante in componente_gigante:
    for indice in range(len(red_vial.adj_dist[nodo_origen_gigante])):
        nodo_destino = red_vial.adj_dist[nodo_origen_gigante][indice][1]

        if nodo_destino in componente_gigante:
            adyacencias_distancia_gigante[nodo_origen_gigante].append(
                red_vial.adj_dist[nodo_origen_gigante][indice]
            )

# Para pruebas iniciales del avance se utiliza una muestra reducida de 50 nodos.
nodos_muestra = list(componente_gigante)[:50]

tiempo_inicio = time.time()

distancia_maxima = 0
par_nodos_mas_lejanos = (None, None)

dijkstra_componente_gigante = Dijkstra(adyacencias_distancia_gigante)

for nodo_inicio in nodos_muestra:
    distancias_desde_nodo = dijkstra_componente_gigante.ejecutar(nodo_inicio)

    for nodo_destino in distancias_desde_nodo:
        if (
            distancias_desde_nodo[nodo_destino] != float("inf")
            and distancias_desde_nodo[nodo_destino] > distancia_maxima
        ):
            distancia_maxima = distancias_desde_nodo[nodo_destino]
            par_nodos_mas_lejanos = (nodo_inicio, nodo_destino)

tiempo_fin = time.time()

print(f"[3] Diametro vial (muestra 5 nodos)")
print(
    f"    Par mas distante: "
    f"{par_nodos_mas_lejanos[0]} -> {par_nodos_mas_lejanos[1]}"
)

if par_nodos_mas_lejanos[0] in red_vial.nodos_coords:
    print(
        f"    Coordenadas nodo {par_nodos_mas_lejanos[0]}: "
        f"{red_vial.nodos_coords[par_nodos_mas_lejanos[0]]}"
    )

if par_nodos_mas_lejanos[1] in red_vial.nodos_coords:
    print(
        f"    Coordenadas nodo {par_nodos_mas_lejanos[1]}: "
        f"{red_vial.nodos_coords[par_nodos_mas_lejanos[1]]}"
    )

print(f"    Distancia: {distancia_maxima / 1000:.2f} km")
print(f"    Tiempo de ejecucion: {tiempo_fin - tiempo_inicio:.4f} segundos\n")

tiempo_inicio = time.time()

algoritmo_kruskal = Kruskal()

distancia_total_mst, cantidad_aristas_mst = algoritmo_kruskal.ejecutar(
    list(componente_gigante),
    red_vial.aristas_lista,
    componente_gigante
)

tiempo_fin = time.time()

print(f"[4] Red de emergencia minima (Kruskal + Union-Find)")
print(f"    Nodos cubiertos:     {len(componente_gigante)}")
print(f"    Aristas en MST:      {cantidad_aristas_mst}")
print(f"    Distancia total:     {distancia_total_mst / 1000:.2f} km")
print(f"    Tiempo de ejecucion: {tiempo_fin - tiempo_inicio:.4f} segundos\n")