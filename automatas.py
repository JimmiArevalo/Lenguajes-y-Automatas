"""Autómatas finitos deterministas (AFD) del sistema.

Replican exactamente los modelos de los archivos .jflap:
  - AFD_CODIGO : valida el código de una orden de recolección (R-Z-DDD).
  - AFD_CICLO  : modela el ciclo de vida de una orden de recolección.
"""

ZONAS = "ULGFS"          # Ubaté, Lenguazaque, Guachetá, Fúquene, Susa
DIGITOS = "0123456789"

# ---- AFD 1: código de orden  ->  R-<zona>-<d><d><d> -----------------------
AFD_CODIGO = {
    "inicial": "q0",
    "finales": {"q7"},
    "delta": {
        **{("q0", "R"): "q1"},
        **{("q1", "-"): "q2"},
        **{("q2", z): "q3" for z in ZONAS},
        **{("q3", "-"): "q4"},
        **{("q4", d): "q5" for d in DIGITOS},
        **{("q5", d): "q6" for d in DIGITOS},
        **{("q6", d): "q7" for d in DIGITOS},
    },
}

# ---- AFD 2: ciclo de vida de la orden --------------------------------------
# a=asignar vehículo, i=iniciar ruta, r=recoger lote en finca,
# c=control de calidad aprobado, x=rechazo por calidad,
# e=entregar en planta, k=cancelar
NOMBRES_CICLO = {
    "q0": "Programada", "q1": "Asignada", "q2": "EnRuta",
    "q3": "Recolectando", "q4": "Verificada", "q5": "Entregada",
    "q6": "Cancelada", "q7": "Rechazada",
}
AFD_CICLO = {
    "inicial": "q0",
    "finales": {"q5", "q6", "q7"},
    "delta": {
        ("q0", "a"): "q1", ("q0", "k"): "q6",
        ("q1", "i"): "q2", ("q1", "k"): "q6",
        ("q2", "r"): "q3", ("q2", "k"): "q6",
        ("q3", "r"): "q3", ("q3", "c"): "q4", ("q3", "x"): "q7",
        ("q4", "e"): "q5",
    },
}


def simular(afd, cadena):
    """Devuelve (aceptada, estado_final). Rechaza si falta transición."""
    estado = afd["inicial"]
    for simbolo in cadena:
        estado = afd["delta"].get((estado, simbolo))
        if estado is None:
            return False, None
    return estado in afd["finales"], estado


def codigo_valido(codigo: str) -> bool:
    return simular(AFD_CODIGO, codigo)[0]


class OrdenRecoleccion:
    """Orden cuyo estado solo puede cambiar por transiciones válidas del AFD."""

    def __init__(self, codigo: str):
        if not codigo_valido(codigo):
            raise ValueError(f"Código inválido: {codigo!r}")
        self.codigo = codigo
        self.estado = AFD_CICLO["inicial"]
        self.historial = [self.estado]

    def evento(self, simbolo: str) -> str:
        siguiente = AFD_CICLO["delta"].get((self.estado, simbolo))
        if siguiente is None:
            raise ValueError(
                f"Evento '{simbolo}' no permitido en estado "
                f"{NOMBRES_CICLO[self.estado]}")
        self.estado = siguiente
        self.historial.append(siguiente)
        return NOMBRES_CICLO[siguiente]

    @property
    def terminada(self) -> bool:
        return self.estado in AFD_CICLO["finales"]
