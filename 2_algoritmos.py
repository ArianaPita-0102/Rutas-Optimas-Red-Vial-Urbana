import pandas as pd
import heapq
from collections import defaultdict
from pyproj import Transformer

# el dataset tiene coordenadas en metros, las convierto a lat/lon para que se entiendan
transformer = Transformer.from_crs("epsg:32719", "epsg:4326", always_xy=True)

def a_latlon(x, y):
    lon, lat = transformer.transform(x, y)
    return round(lat, 6), round(lon, 6)


# CLASE: RedVial
# la base de todo — lee los CSV y arma el grafo en memoria
# sin esta los algoritmos no tienen donde trabajar
# guarda dos listas de adyacencia: una por distancia y otra por tiempo
# porque dijkstra la uso dos veces en el bonus (una por km y otra por minutos)
class RedVial:
    def __init__(self):
        self.adyacencia_distancia = defaultdict(list)  # adyacencia_distancia[nodo] = [(metros, vecino), ...]
        self.adyacencia_tiempo = defaultdict(list)      # adyacencia_tiempo[nodo] = [(minutos, vecino), ...]
        self.lista_aristas = []    # lista plana de aristas que kruskal necesita para ordenar
        self.conjunto_nodos = set() # solo nodos que tienen al menos una calle vehicular
        self.coordenadas = {}       # coordenadas geograficas de cada interseccion

    def cargar_nodos(self, path):
        # leo nodes.csv y guardo las coordenadas convertidas a lat/lon
        # no las usan los algoritmos, solo las muestro en los resultados
        tabla_nodos = pd.read_csv(path)
        for _, fila in tabla_nodos.iterrows():
            id_nodo = int(fila["node_id"])
            self.coordenadas[id_nodo] = a_latlon(float(fila["lon"]), float(fila["lat"]))
        print(f"Nodos cargados: {len(self.coordenadas)}")

    def cargar_aristas(self, path):
        # leo edges_limpio.csv y construyo el grafo dirigido
        # si oneway=0 la calle es de doble sentido, agrego la arista en ambas direcciones
        tabla_aristas = pd.read_csv(path)
        for _, fila in tabla_aristas.iterrows():
            nodo_origen  = int(fila["from_id"])
            nodo_destino = int(fila["to_id"])
            metros       = fila["distance_m"]
            minutos      = fila["tiempo_min"]

            # arista dirigida origen -> destino siempre
            self.adyacencia_distancia[nodo_origen].append((metros, nodo_destino))
            self.adyacencia_tiempo[nodo_origen].append((minutos, nodo_destino))
            self.lista_aristas.append((metros, nodo_origen, nodo_destino))
            self.conjunto_nodos.add(nodo_origen)
            self.conjunto_nodos.add(nodo_destino)

            # si es doble sentido agrego tambien destino -> origen
            if fila["oneway"] == 0:
                self.adyacencia_distancia[nodo_destino].append((metros, nodo_origen))
                self.adyacencia_tiempo[nodo_destino].append((minutos, nodo_origen))
                self.lista_aristas.append((metros, nodo_destino, nodo_origen))

        print(f"Grafo cargado — nodos: {len(self.conjunto_nodos)}, aristas: {len(tabla_aristas)}\n")


# CLASE: UnionFind
# la uso para dos cosas en el proyecto:
# 1. detectar islas viales — agrupa nodos conectados y cuenta cuantos grupos hay
# 2. dentro de kruskal — detecta si agregar una arista formaria ciclo o no
# con path compression y union by rank para que sea casi O(1) por operacion
class UnionFind:
    def __init__(self, nodos):
        # cada nodo empieza siendo su propio representante
        self.representante = {nodo: nodo for nodo in nodos}
        self.altura = {nodo: 0 for nodo in nodos}

    def find(self, nodo):
        # busca el representante del grupo
        # path compression: en cada busqueda aplana el arbol para que las futuras sean mas rapidas
        if self.representante[nodo] != nodo:
            self.representante[nodo] = self.find(self.representante[nodo])
        return self.representante[nodo]

    def union(self, nodo_a, nodo_b):
        # une los grupos de nodo_a y nodo_b
        # retorna false si ya estaban en el mismo grupo (formaria ciclo)
        # retorna true si los uno exitosamente
        rep_a = self.find(nodo_a)
        rep_b = self.find(nodo_b)
        if rep_a == rep_b:
            return False  # mismo grupo, no hago nada
        # union by rank: el arbol mas bajo se adjunta al mas alto
        if self.altura[rep_a] < self.altura[rep_b]:
            rep_a, rep_b = rep_b, rep_a
        self.representante[rep_b] = rep_a
        if self.altura[rep_a] == self.altura[rep_b]:
            self.altura[rep_a] += 1
        return True


# CLASE: Dijkstra
# la uso tres veces en el proyecto:
# 1. objetivo 1 — alcance vehicular con limite de 5 km
# 2. objetivo 3 — diametro vial desde 500 nodos de muestra
# 3. bonus — dos veces entre el mismo par, una por distancia y otra por tiempo
# usa un min-heap para siempre procesar primero el nodo mas cercano
# complejidad: O((V + E) log V)
class Dijkstra:
    def __init__(self, adyacencia):
        self.adyacencia = adyacencia  # recibe adyacencia_distancia o adyacencia_tiempo

    def ejecutar(self, nodo_origen, limite=None):
        # distancia_minima[v] = menor distancia conocida desde origen hasta v
        distancia_minima = defaultdict(lambda: float('inf'))
        distancia_minima[nodo_origen] = 0
        heap = [(0, nodo_origen)]  # min-heap con (distancia acumulada, nodo)

        while heap:
            distancia_actual = heap[0][0]
            nodo_actual      = heap[0][1]
            heapq.heappop(heap)  # saca el nodo mas cercano — O(log N)

            # si ya encontramos una ruta mejor antes, ignoramos esta entrada
            if distancia_actual > distancia_minima[nodo_actual]:
                continue

            for i in range(len(self.adyacencia[nodo_actual])):
                peso_arista = self.adyacencia[nodo_actual][i][0]
                nodo_vecino = self.adyacencia[nodo_actual][i][1]

                # si hay limite y lo superamos, no exploramos por ahi
                if limite is not None and distancia_minima[nodo_actual] + peso_arista > limite:
                    continue

                # si pasar por nodo_actual mejora la distancia a nodo_vecino, actualizamos
                nueva_distancia = distancia_minima[nodo_actual] + peso_arista
                if nueva_distancia < distancia_minima[nodo_vecino]:
                    distancia_minima[nodo_vecino] = nueva_distancia
                    heapq.heappush(heap, (nueva_distancia, nodo_vecino))  # O(log N)

        return distancia_minima


# CLASE: Kruskal
# la uso para el objetivo 4 — red de emergencia minima (MST)
# conecta todos los nodos de la componente gigante con la menor distancia total posible
# ordena aristas de menor a mayor y agrega las que no forman ciclo
# para detectar ciclos usa UnionFind internamente
# elegi kruskal sobre prim porque el grafo es disperso y union-find ya estaba hecho
# complejidad: O(E log E) por el ordenamiento
class Kruskal:
    def ejecutar(self, nodos_gigante, lista_aristas, conjunto_gigante):
        # me quedo solo con aristas donde ambos extremos estan en la componente gigante
        aristas_gigante = [(metros, origen, destino)
                           for metros, origen, destino in lista_aristas
                           if origen in conjunto_gigante and destino in conjunto_gigante]
        aristas_gigante.sort()  # ordeno de menor a mayor distancia — O(E log E)

        uf = UnionFind(nodos_gigante)
        distancia_total = 0
        cantidad_aristas_mst = 0

        for i in range(len(aristas_gigante)):
            metros  = aristas_gigante[i][0]
            origen  = aristas_gigante[i][1]
            destino = aristas_gigante[i][2]
            # si union retorna true no hay ciclo, agrego al MST
            # si retorna false ya estaban conectados, descarto
            if uf.union(origen, destino):
                distancia_total += metros
                cantidad_aristas_mst += 1

        return distancia_total, cantidad_aristas_mst