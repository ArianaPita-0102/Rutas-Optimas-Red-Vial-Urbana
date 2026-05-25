import pandas as pd

nodos = pd.read_csv("nodes.csv")
aristas = pd.read_csv("edges.csv")

print(f"Antes — nodos: {len(nodos)}, aristas: {len(aristas)}")

# solo vias por donde circulan vehiculos
vias_ok = ["motorway","motorway_link","trunk","trunk_link",
           "primary","primary_link","secondary","secondary_link",
           "tertiary","tertiary_link","residential","unclassified",
           "living_street","service"]
aristas = aristas[aristas["fclass"].isin(vias_ok)].copy()

# oneway: habia un valor "oneway" como texto, lo normalizamos
aristas["oneway"] = aristas["oneway"].apply(
    lambda v: 1 if str(v).strip() in ["1","T","yes","true","oneway"] else 0
)

# maxspeed: 0 significa sin dato, imputamos por tipo de via
vel = {"motorway":100,"motorway_link":80,"trunk":80,"trunk_link":60,
       "primary":60,"primary_link":50,"secondary":50,"secondary_link":40,
       "tertiary":40,"tertiary_link":30,"residential":30,
       "unclassified":30,"living_street":20,"service":20}

aristas["maxspeed"] = aristas.apply(
    lambda r: vel.get(r["fclass"], 30) if r["maxspeed"] == 0 else r["maxspeed"], axis=1
)

# tiempo en minutos = (distancia en km) / velocidad * 60
aristas["tiempo_min"] = (aristas["distance_m"] / 1000) / aristas["maxspeed"] * 60

# duplicados por par origen-destino
antes = len(aristas)
aristas = aristas.drop_duplicates(subset=["from_id","to_id"])
print(f"Duplicados eliminados: {antes - len(aristas)}")

# aristas cuyos nodos no existen en nodes.csv
nodos_validos = set(nodos["node_id"])
aristas = aristas[aristas["from_id"].isin(nodos_validos) & aristas["to_id"].isin(nodos_validos)]

aristas.to_csv("edges_limpio.csv", index=False)
nodos.to_csv("nodes_limpio.csv", index=False)

print(f"Despues — nodos: {len(nodos)}, aristas: {len(aristas)}")
print("Archivos guardados: edges_limpio.csv, nodes_limpio.csv")