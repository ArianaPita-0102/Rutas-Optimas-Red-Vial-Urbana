import time
from collections import defaultdict
from algoritmos import RedVial, UnionFind, Dijkstra, Kruskal

red_vial = RedVial()
red_vial.cargar_nodos("nodes.csv")
red_vial.cargar_aristas("edges_limpio.csv")

nodo_origen = list(red_vial.conjunto_nodos)[0]

#
print(f"Verificacion de coordenadas: {red_vial.coordenadas[nodo_origen]}")

# [1] Alcance vehicular
tiempo_inicio = time.time()

algoritmo_dijkstra = Dijkstra(red_vial.adyacencia_distancia)
distancias, _ = algoritmo_dijkstra.ejecutar(nodo_origen, limite=5000)

nodos_alcanzables = [
    nodo for nodo in distancias
    if distancias[nodo] <= 5000
]

tiempo_fin = time.time()

print(f"[1] Alcance vehicular desde nodo {nodo_origen}")
if nodo_origen in red_vial.coordenadas:
    print(f"    Coordenadas origen: {red_vial.coordenadas[nodo_origen]}")
print(f"    Nodos alcanzables en <= 5 km: {len(nodos_alcanzables)}")
print(f"    Tiempo de ejecucion: {tiempo_fin - tiempo_inicio:.4f} segundos\n")

# [2] Islas viales
tiempo_inicio = time.time()

estructura_union_find = UnionFind(red_vial.conjunto_nodos)

for indice in range(len(red_vial.lista_aristas)):
    _, nodo_a, nodo_b = red_vial.lista_aristas[indice]
    estructura_union_find.union(nodo_a, nodo_b)

componentes_por_representante = defaultdict(list)
for nodo in red_vial.conjunto_nodos:
    representante = estructura_union_find.find(nodo)
    componentes_por_representante[representante].append(nodo)

componentes_conectadas = sorted(
    componentes_por_representante.values(),
    key=len,
    reverse=True
)

tiempo_fin = time.time()

componente_gigante = set(componentes_conectadas[0])

suma_grados = 0
for nodo in componente_gigante:
    suma_grados += len(red_vial.adyacencia_distancia[nodo])
grado_promedio = suma_grados / len(componente_gigante)

print(f"[2] Islas viales")
print(f"    Total de componentes:  {len(componentes_conectadas)}")
print(f"    Componente gigante:    {len(componentes_conectadas[0])} nodos")
print(f"    Islas pequeñas:        {len(componentes_conectadas) - 1}")
print(f"    Grado promedio:        {grado_promedio:.2f}")
print(f"    Tiempo de ejecucion:   {tiempo_fin - tiempo_inicio:.4f} segundos\n")

# [3] Diámetro vial
adyacencias_distancia_gigante = defaultdict(list)
for nodo_g in componente_gigante:
    for peso, vecino in red_vial.adyacencia_distancia[nodo_g]:
        if vecino in componente_gigante:
            adyacencias_distancia_gigante[nodo_g].append((peso, vecino))

nodos_muestra = list(componente_gigante)[:500]

tiempo_inicio = time.time()

distancia_maxima = 0
par_nodos_mas_lejanos = (None, None)

dijkstra_gigante = Dijkstra(adyacencias_distancia_gigante)

for nodo_inicio in nodos_muestra:
    distancias_desde_nodo, _ = dijkstra_gigante.ejecutar(nodo_inicio)
    for nodo_destino, dist in distancias_desde_nodo.items():
        if dist != float("inf") and dist > distancia_maxima:
            distancia_maxima = dist
            par_nodos_mas_lejanos = (nodo_inicio, nodo_destino)

tiempo_fin = time.time()

print(f"[3] Diametro vial (aproximado — muestra 500 nodos de la componente gigante)")
print(f"    Nota: ejecutar Dijkstra desde los {len(componente_gigante)} nodos")
print(f"    de la componente gigante es computacionalmente inviable en tiempo")
print(f"    razonable. La muestra de 500 nodos entrega un limite inferior del")
print(f"    diametro real.")
print(f"    Par mas distante: {par_nodos_mas_lejanos[0]} -> {par_nodos_mas_lejanos[1]}")
if par_nodos_mas_lejanos[0] in red_vial.coordenadas:
    print(f"    Coordenadas nodo {par_nodos_mas_lejanos[0]}: {red_vial.coordenadas[par_nodos_mas_lejanos[0]]}")
if par_nodos_mas_lejanos[1] in red_vial.coordenadas:
    print(f"    Coordenadas nodo {par_nodos_mas_lejanos[1]}: {red_vial.coordenadas[par_nodos_mas_lejanos[1]]}")
print(f"    Distancia: {distancia_maxima / 1000:.2f} km")
print(f"    Tiempo de ejecucion: {tiempo_fin - tiempo_inicio:.4f} segundos\n")

# [4] Red de emergencia mínima
tiempo_inicio = time.time()

algoritmo_kruskal = Kruskal()
distancia_total_mst, cantidad_aristas_mst = algoritmo_kruskal.ejecutar(
    list(componente_gigante),
    red_vial.lista_aristas,
    componente_gigante
)

tiempo_fin = time.time()

print(f"[4] Red de emergencia minima (Kruskal + Union-Find)")
print(f"    Nodos cubiertos:     {len(componente_gigante)}")
print(f"    Aristas en MST:      {cantidad_aristas_mst}")
print(f"    Distancia total:     {distancia_total_mst / 1000:.2f} km")
print(f"    Tiempo de ejecucion: {tiempo_fin - tiempo_inicio:.4f} segundos\n")

# [BONUS] Comparación distancia vs tiempo
nodo_a, nodo_b = par_nodos_mas_lejanos

adyacencias_tiempo_gigante = defaultdict(list)
for nodo_g in componente_gigante:
    for peso, vecino in red_vial.adyacencia_tiempo[nodo_g]:
        if vecino in componente_gigante:
            adyacencias_tiempo_gigante[nodo_g].append((peso, vecino))

tiempo_inicio = time.time()
dijkstra_dist = Dijkstra(adyacencias_distancia_gigante)
distancias_d, previo_d = dijkstra_dist.ejecutar(nodo_a)
camino_d = dijkstra_dist.reconstruir_camino(previo_d, nodo_b)
tiempo_fin = time.time()
tiempo_ejec_dist = tiempo_fin - tiempo_inicio

tiempo_inicio = time.time()
dijkstra_time = Dijkstra(adyacencias_tiempo_gigante)
distancias_t, previo_t = dijkstra_time.ejecutar(nodo_a)
camino_t = dijkstra_time.reconstruir_camino(previo_t, nodo_b)
tiempo_fin = time.time()
tiempo_ejec_time = tiempo_fin - tiempo_inicio

dist_km_d = distancias_d[nodo_b] / 1000

dist_km_t = 0
for i in range(len(camino_t) - 1):
    u = camino_t[i]
    v = camino_t[i + 1]
    for peso, vecino in red_vial.adyacencia_distancia[u]:
        if vecino == v:
            dist_km_t += peso
            break
dist_km_t = dist_km_t / 1000

tiempo_min_d = 0
for i in range(len(camino_d) - 1):
    u = camino_d[i]
    v = camino_d[i + 1]
    for peso, vecino in red_vial.adyacencia_tiempo[u]:
        if vecino == v:
            tiempo_min_d += peso
            break

tiempo_min_t = distancias_t[nodo_b]

print(f"[BONUS] Comparacion distancia vs tiempo")
print(f"    Par de nodos: {nodo_a} -> {nodo_b}\n")
print(f"    {'Metrica':<25} {'Ruta DISTANCIA':>15} {'Ruta TIEMPO':>15} {'Diferencia':>12}")
print(f"    {'-'*67}")
print(f"    {'Distancia recorrida (km)':<25} {dist_km_d:>15.2f} {dist_km_t:>15.2f} {abs(dist_km_d - dist_km_t):>12.2f}")
print(f"    {'Tiempo estimado (min)':<25} {tiempo_min_d:>15.2f} {tiempo_min_t:>15.2f} {abs(tiempo_min_d - tiempo_min_t):>12.2f}")
print(f"    {'Nodos en la ruta':<25} {len(camino_d):>15} {len(camino_t):>15} {abs(len(camino_d) - len(camino_t)):>12}")
print(f"    {'Tiempo de ejecucion (s)':<25} {tiempo_ejec_dist:>15.4f} {tiempo_ejec_time:>15.4f}")