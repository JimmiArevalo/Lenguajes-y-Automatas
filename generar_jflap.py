"""Genera los archivos .jflap (formato XML de JFLAP 7) desde los AFD de automatas.py
y los vuelve a leer para comprobar que el archivo equivale al modelo."""
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from automatas import AFD_CODIGO, AFD_CICLO, NOMBRES_CICLO, simular

def escribir(afd, ruta, nombres=None, columnas=4):
    estados = sorted({afd["inicial"], *afd["finales"],
                      *[s for (s, _) in afd["delta"]], *afd["delta"].values()},
                     key=lambda q: int(q[1:]))
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
           '<structure>&#13;', '\t<type>fa</type>&#13;', '\t<automaton>&#13;']
    for i, q in enumerate(estados):
        x, y = 80 + 150 * (i % columnas), 80 + 130 * (i // columnas)
        nombre = nombres[q] if nombres else q
        out.append(f'\t\t<state id="{q[1:]}" name="{escape(nombre)}">&#13;')
        out.append(f'\t\t\t<x>{x}.0</x>&#13;\n\t\t\t<y>{y}.0</y>&#13;')
        if q == afd["inicial"]: out.append('\t\t\t<initial/>&#13;')
        if q in afd["finales"]: out.append('\t\t\t<final/>&#13;')
        out.append('\t\t</state>&#13;')
    for (o, s), d in afd["delta"].items():
        out.append(f'\t\t<transition>&#13;\n\t\t\t<from>{o[1:]}</from>&#13;\n'
                   f'\t\t\t<to>{d[1:]}</to>&#13;\n\t\t\t<read>{escape(s)}</read>&#13;\n\t\t</transition>&#13;')
    out += ['\t</automaton>&#13;', '</structure>']
    open(ruta, "w", encoding="utf-8").write("\n".join(out))

def releer(ruta):
    r = ET.parse(ruta).getroot().find("automaton")
    ini, fin, delta = None, set(), {}
    for s in r.findall("state"):
        q = "q" + s.get("id")
        if s.find("initial") is not None: ini = q
        if s.find("final") is not None: fin.add(q)
    for t in r.findall("transition"):
        delta[("q" + t.find("from").text, t.find("read").text)] = "q" + t.find("to").text
    return {"inicial": ini, "finales": fin, "delta": delta}

if __name__ == "__main__":
    escribir(AFD_CODIGO, "../jflap/AFD_codigo_orden.jflap")
    escribir(AFD_CICLO, "../jflap/AFD_ciclo_vida_orden.jflap", NOMBRES_CICLO)
    for orig, f in [(AFD_CODIGO, "AFD_codigo_orden"), (AFD_CICLO, "AFD_ciclo_vida_orden")]:
        assert releer(f"../jflap/{f}.jflap") == orig, f
    print("OK: archivos .jflap releídos y equivalentes a los modelos")
