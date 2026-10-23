import itertools, re, unittest
from automatas import (AFD_CODIGO, AFD_CICLO, simular, codigo_valido,
                       OrdenRecoleccion)
from grafo_vial import construir_grafo, PLANTA, dividir_por_capacidad, OFERTA_LITROS


class TestAutomatas(unittest.TestCase):
    def test_codigo(self):
        for ok in ["R-U-001", "R-S-999"]:
            self.assertTrue(codigo_valido(ok))
        for mal in ["", "R-X-001", "R-U-01", "R-U-0012", "r-U-001", "R-U001"]:
            self.assertFalse(codigo_valido(mal))

    def test_ciclo_equivale_a_regex(self):
        rx = re.compile(r"k|ak|aik|air+(ce|x)")
        for n in range(0, 8):
            for t in itertools.product("airckxe", repeat=n):
                s = "".join(t)
                self.assertEqual(simular(AFD_CICLO, s)[0], bool(rx.fullmatch(s)), s)

    def test_orden_invalida(self):
        o = OrdenRecoleccion("R-L-100")
        with self.assertRaises(ValueError):
            o.evento("e")          # no se puede entregar sin haber recogido
        with self.assertRaises(ValueError):
            OrdenRecoleccion("XX")


class TestGrafo(unittest.TestCase):
    def test_conexo(self):
        import networkx as nx
        self.assertTrue(nx.is_connected(construir_grafo()))

    def test_capacidad(self):
        for v in dividir_por_capacidad(list(OFERTA_LITROS), 6000):
            self.assertLessEqual(sum(OFERTA_LITROS[x] for x in v), 6000)


if __name__ == "__main__":
    unittest.main()
