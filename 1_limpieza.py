import pandas as pd

nodos = pd.read_csv("nodes.csv")
aristas = pd.read_csv("edges.csv")

print(f"Antes — nodos: {len(nodos)}, aristas: {len(aristas)}")

vias_ok = ["motorway","motorway_link","trunk","trunk_link",
           "primary","primary_link","secondary","secondary_link",
           "tertiary","tertiary_link","residential","unclassified",
           "living_street","service"]
aristas = aristas[aristas["fclass"].isin(vias_ok)].copy()

aristas["oneway"] = aristas["oneway"].apply(
    lambda v: 1 if str(v).strip() in ["1","T","yes","true","oneway"] else 0
)

def limpiar_velocidad(v):
    try:
        return float(str(v).replace("km/h", "").strip())
    except:
        return 0

aristas["maxspeed"] = aristas["maxspeed"].apply(limpiar_velocidad)

vel = {"motorway":100,"motorway_link":80,"trunk":80,"trunk_link":60,
       "primary":60,"primary_link":50,"secondary":50,"secondary_link":40,
       "tertiary":40,"tertiary_link":30,"residential":30,
       "unclassified":30,"living_street":20,"service":20}

aristas["maxspeed"] = aristas.apply(
    lambda r: vel.get(r["fclass"], 30) if r["maxspeed"] == 0 else r["maxspeed"], axis=1
)

aristas["tiempo_min"] = (aristas["distance_m"] / 1000) / aristas["maxspeed"] * 60

antes = len(aristas)
aristas = aristas.drop_duplicates(subset=["from_id","to_id"])
print(f"Duplicados eliminados: {antes - len(aristas)}")

nodos_validos = set(nodos["node_id"])
aristas = aristas[aristas["from_id"].isin(nodos_validos) & aristas["to_id"].isin(nodos_validos)]

aristas.to_csv("edges_limpio.csv", index=False)

print(f"\n=== IMPACTO DE LIMPIEZA ===")
print(f"Aristas originales:         588485")
print(f"Eliminadas por tipo de via: {588485 - 336553}")
print(f"Eliminadas por duplicado:   {antes - len(aristas)}")
print(f"Aristas finales:            {len(aristas)}")
print(f"Porcentaje descartado:      {(1 - len(aristas)/588485)*100:.1f}%")
print(f"Guardado: edges_limpio.csv")