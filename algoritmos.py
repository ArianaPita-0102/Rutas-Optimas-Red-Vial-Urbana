import pandas as pd
import heapq
from collections import defaultdict
from pyproj import Transformer

transformer = Transformer.from_crs("epsg:32719", "epsg:4326", always_xy=True)

def a_latlon(x, y):
    lon, lat = transformer.transform(x, y)
    return round(lat, 6), round(lon, 6)


class RedVial:
    def __init__(self):
        self.adyacencia_distancia = defaultdict(list)
        self.adyacencia_tiempo = defaultdict(list)
        self.lista_aristas = []
        self.conjunto_nodos = set()
        self.coordenadas = {}

    def cargar_nodos(self, path):
        tabla_nodos = pd.read_csv(path)
        for _, fila in tabla_nodos.iterrows():
            id_nodo = int(fila["node_id"])
            self.coordenadas[id_nodo] = a_latlon(float(fila["lon"]), float(fila["lat"]))
        print(f"Nodos cargados: {len(self.coordenadas)}")

    def cargar_aristas(self, path):
        tabla_aristas = pd.read_csv(path)
        for _, fila in tabla_aristas.iterrows():
            nodo_origen = int(fila["from_id"])
            nodo_destino = int(fila["to_id"])
            metros = fila["distance_m"]
            minutos = fila["tiempo_min"]

            self.adyacencia_distancia[nodo_origen].append((metros, nodo_destino))
            self.adyacencia_tiempo[nodo_origen].append((minutos, nodo_destino))
            self.lista_aristas.append((metros, nodo_origen, nodo_destino))
            self.conjunto_nodos.add(nodo_origen)
            self.conjunto_nodos.add(nodo_destino)

            if fila["oneway"] == 0:
                self.adyacencia_distancia[nodo_destino].append((metros, nodo_origen))
                self.adyacencia_tiempo[nodo_destino].append((minutos, nodo_origen))

        print(f"Grafo cargado — nodos: {len(self.conjunto_nodos)}, aristas: {len(tabla_aristas)}\n")


class UnionFind:
    def __init__(self, nodos):
        self.representante = {nodo: nodo for nodo in nodos}
        self.altura = {nodo: 0 for nodo in nodos}

    def find(self, nodo):
        if self.representante[nodo] != nodo:
            self.representante[nodo] = self.find(self.representante[nodo])
        return self.representante[nodo]

    def union(self, nodo_a, nodo_b):
        rep_a = self.find(nodo_a)
        rep_b = self.find(nodo_b)

        if rep_a == rep_b:
            return False

        if self.altura[rep_a] < self.altura[rep_b]:
            rep_a, rep_b = rep_b, rep_a

        self.representante[rep_b] = rep_a

        if self.altura[rep_a] == self.altura[rep_b]:
            self.altura[rep_a] += 1

        return True


class Dijkstra:
    def __init__(self, adyacencia):
        self.adyacencia = adyacencia

    def ejecutar(self, nodo_origen, limite=None):
        distancia_minima = defaultdict(lambda: float('inf'))
        distancia_minima[nodo_origen] = 0
        previo = {nodo_origen: None}

        heap = [(0, nodo_origen)]

        while heap:
            distancia_actual = heap[0][0]
            nodo_actual = heap[0][1]
            heapq.heappop(heap)

            if distancia_actual > distancia_minima[nodo_actual]:
                continue

            for i in range(len(self.adyacencia[nodo_actual])):
                peso_arista = self.adyacencia[nodo_actual][i][0]
                nodo_vecino = self.adyacencia[nodo_actual][i][1]

                if limite is not None and distancia_minima[nodo_actual] + peso_arista > limite:
                    continue

                nueva_distancia = distancia_minima[nodo_actual] + peso_arista

                if nueva_distancia < distancia_minima[nodo_vecino]:
                    distancia_minima[nodo_vecino] = nueva_distancia
                    previo[nodo_vecino] = nodo_actual
                    heapq.heappush(heap, (nueva_distancia, nodo_vecino))

        return distancia_minima, previo

    def reconstruir_camino(self, previo, nodo_destino):
        camino = []
        nodo_actual = nodo_destino
        while nodo_actual is not None:
            camino.append(nodo_actual)
            nodo_actual = previo.get(nodo_actual)
        camino.reverse()
        return camino


class Kruskal:
    def ejecutar(self, nodos_gigante, lista_aristas, conjunto_gigante):
        visitadas = set()
        aristas_gigante = []

        for metros, origen, destino in lista_aristas:
            if origen in conjunto_gigante and destino in conjunto_gigante:
                clave = tuple(sorted((origen, destino)))
                if clave not in visitadas:
                    visitadas.add(clave)
                    aristas_gigante.append((metros, origen, destino))

        aristas_gigante.sort()

        uf = UnionFind(nodos_gigante)

        distancia_total = 0
        cantidad_aristas_mst = 0

        for i in range(len(aristas_gigante)):
            metros = aristas_gigante[i][0]
            origen = aristas_gigante[i][1]
            destino = aristas_gigante[i][2]

            if uf.union(origen, destino):
                distancia_total += metros
                cantidad_aristas_mst += 1

        return distancia_total, cantidad_aristas_mst