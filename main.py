"""Prototipo integrado: AFD + grafo (NetworkX) + IA (scikit-learn)."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network

from automatas import OrdenRecoleccion, codigo_valido
from grafo_vial import (PLANTA, OFERTA_LITROS, construir_grafo, asignar_pesos,
                        ruta_mas_corta, ruta_recoleccion, dividir_por_capacidad)
from modelo_ia import entrenar


def main():
    # 1) Capa de validación (AFD)
    orden = OrdenRecoleccion("R-G-012")
    for ev in "airrce":
        orden.evento(ev)
    print("Orden", orden.codigo, "-> estado final:", orden.estado, "terminada:", orden.terminada)

    # 2) Capa de IA
    modelo, metricas, _ = entrenar()
    for nombre, (mae, r2) in metricas.items():
        print(f"{nombre}: MAE={mae:.2f} min  R2={r2:.3f}")

    # 3) Capa de grafos: comparación de escenarios
    g = construir_grafo()
    resultados = {}
    for etiqueta, hora, lluvia in [("Seco, 10:00", 10, 0.0), ("Lluvia fuerte, 7:00", 7, 0.9)]:
        asignar_pesos(g, modelo, hora, lluvia)
        camino, costo = ruta_mas_corta(g, PLANTA, "Carmen de Carupa")
        viajes = dividir_por_capacidad(list(OFERTA_LITROS), 6000)
        plan = []
        for v in viajes:
            ciclo, c = ruta_recoleccion(g, v)
            plan.append({"paradas": ciclo, "minutos": round(c, 1),
                         "litros": sum(OFERTA_LITROS[x] for x in v)})
        resultados[etiqueta] = {"dijkstra": camino, "dijkstra_min": round(costo, 1), "viajes": plan}
        print("\n==", etiqueta)
        print(" Planta -> Carmen de Carupa:", " > ".join(camino), f"({costo:.1f} min)")
        for i, p in enumerate(plan, 1):
            print(f" Viaje {i}: {' > '.join(p['paradas'])} | {p['litros']} L | {p['minutos']} min")
    json.dump(resultados, open("resultados.json", "w"), ensure_ascii=False, indent=2)

    # 4) Visualización (matplotlib + PyVis) para el escenario con lluvia
    pos = nx.spring_layout(g, seed=3, weight=None)
    plt.figure(figsize=(9, 6))
    nx.draw_networkx(g, pos, node_color="#cfe8d5", edge_color="#888", font_size=8, node_size=1400)
    nx.draw_networkx_edge_labels(g, pos, {(u, v): f"{d['min']:.0f}'" for u, v, d in g.edges(data=True)}, font_size=7)
    plt.title("Red vial (minutos predichos, lluvia fuerte 7:00)")
    plt.axis("off"); plt.tight_layout(); plt.savefig("../figuras/grafo_vial.png", dpi=160)
    net = Network(height="600px", width="100%")
    net.from_nx(g)
    net.save_graph("grafo_interactivo.html")


if __name__ == "__main__":
    main()
