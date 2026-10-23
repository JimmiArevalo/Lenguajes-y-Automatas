"""Modelo de la red vial de la provincia de Ubaté como grafo ponderado.

AVISO: las distancias son aproximaciones didácticas (km) para simulación;
deben reemplazarse por mediciones reales (p. ej. API de mapas / INVIAS).
"""
import networkx as nx

PLANTA = "Ubaté (Planta)"

# (origen, destino, km, tipo_via)  tipo_via: 0 = pavimentada, 1 = destapada
ARISTAS = [
    (PLANTA, "Lenguazaque", 22, 0), (PLANTA, "Guachetá", 24, 0),
    (PLANTA, "Fúquene", 14, 0),     (PLANTA, "Susa", 17, 0),
    (PLANTA, "Simijaca", 21, 0),    (PLANTA, "Cucunubá", 18, 0),
    (PLANTA, "Sutatausa", 11, 1),   (PLANTA, "Tausa", 33, 1),
    ("Lenguazaque", "Guachetá", 16, 0), ("Lenguazaque", "Cucunubá", 15, 0),
    ("Guachetá", "Fúquene", 12, 0),     ("Fúquene", "Susa", 9, 0),
    ("Susa", "Simijaca", 7, 0),         ("Cucunubá", "Sutatausa", 10, 1),
    ("Sutatausa", "Tausa", 24, 1),      ("Simijaca", "Carmen de Carupa", 28, 1),
    ("Tausa", "Carmen de Carupa", 15, 1),
]

# Litros diarios disponibles por municipio (simulados)
OFERTA_LITROS = {
    "Lenguazaque": 2200, "Guachetá": 2600, "Fúquene": 1800, "Susa": 1500,
    "Simijaca": 2400, "Cucunubá": 1300, "Sutatausa": 900, "Tausa": 1100,
    "Carmen de Carupa": 800,
}


def construir_grafo() -> nx.Graph:
    g = nx.Graph()
    for u, v, km, via in ARISTAS:
        g.add_edge(u, v, km=km, via=via)
    return g


def asignar_pesos(g: nx.Graph, modelo, hora: int, lluvia: float):
    """Pesos de arista = minutos de viaje predichos por el modelo de IA."""
    for u, v, d in g.edges(data=True):
        d["min"] = float(modelo.predict([[d["km"], d["via"], hora, lluvia]])[0])
    return g


def ruta_mas_corta(g, origen, destino, peso="min"):
    camino = nx.dijkstra_path(g, origen, destino, weight=peso)
    costo = nx.dijkstra_path_length(g, origen, destino, weight=peso)
    return camino, costo


def ruta_recoleccion(g, paradas, peso="min"):
    """Ciclo de recolección planta -> paradas -> planta.

    Usa la clausura métrica (Dijkstra entre pares) y la heurística de TSP
    de NetworkX (recocido simulado) sobre ese grafo completo.
    """
    nodos = [PLANTA] + [p for p in paradas if p != PLANTA]
    dist = dict(nx.all_pairs_dijkstra_path_length(g, weight=peso))
    k = nx.Graph()
    for i, a in enumerate(nodos):
        for b in nodos[i + 1:]:
            k.add_edge(a, b, weight=dist[a][b])
    ciclo = nx.approximation.simulated_annealing_tsp(
        k, "greedy", source=PLANTA, max_iterations=50, N_inner=50, seed=7)
    costo = sum(dist[a][b] for a, b in zip(ciclo, ciclo[1:]))
    return ciclo, costo


def dividir_por_capacidad(paradas, capacidad=6000):
    """Agrupa municipios en viajes (first-fit decreasing) según litros."""
    viajes = []
    for p in sorted(paradas, key=lambda x: -OFERTA_LITROS[x]):
        for v in viajes:
            if sum(OFERTA_LITROS[x] for x in v) + OFERTA_LITROS[p] <= capacidad:
                v.append(p)
                break
        else:
            viajes.append([p])
    return viajes
