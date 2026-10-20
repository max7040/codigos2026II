"""Pruebas del grafo propio y de las métricas."""

import pytest

from analisis.metricas_grafo import (
    celdas_representaciones,
    comparar_representaciones,
    crecimiento_representaciones,
    nodos_por_grado,
)
from estructuras.grafo import ErrorGrafo, Grafo


def red_pequena(dirigido=False):
    g = Grafo(dirigido)
    g.agregar_nodo("a", "equipo")
    g.agregar_nodo("b", "servidor")
    g.agregar_nodo("c", "cuenta")
    g.agregar_conexion("a", "b", peso=2, frecuencia=10, eventos=5)
    g.agregar_conexion("b", "c")
    return g


def test_agregar_y_consultar_nodos():
    g = Grafo()
    assert g.agregar_nodo("  pc-1  ", "equipo") == "pc-1"  # recorta espacios
    assert g.nodos() == ["pc-1"] and g.tipo_nodo("pc-1") == "equipo"
    assert "pc-1" in g and len(g) == 1


@pytest.mark.parametrize("nodo,tipo", [("", "equipo"), ("   ", "equipo"), (5, "equipo"),
                                       ("x" * 65, "equipo"), ("x", "router"), ("x", None)])
def test_nodo_invalido(nodo, tipo):
    with pytest.raises(ErrorGrafo):
        Grafo().agregar_nodo(nodo, tipo)


def test_nodo_duplicado_y_editar_tipo():
    g = Grafo()
    g.agregar_nodo("a")
    with pytest.raises(ErrorGrafo):
        g.agregar_nodo("a")
    g.editar_nodo("a", "servidor")
    assert g.tipo_nodo("a") == "servidor"
    with pytest.raises(ErrorGrafo):
        g.editar_nodo("a", "otro")
    with pytest.raises(ErrorGrafo):
        g.editar_nodo("zzz", "equipo")


def test_conexiones_no_dirigido():
    g = red_pequena()
    assert g.num_conexiones == 2
    assert g.existe_conexion("a", "b") and g.existe_conexion("b", "a")
    assert sorted(g.vecinos("b")) == ["a", "c"]
    assert g.grado("b") == 2 and g.grado("a") == 1
    assert len(g.conexiones()) == 2
    g.editar_conexion("b", "a", eventos=99)  # editar desde el otro extremo
    assert g.obtener_conexion("a", "b")["eventos"] == 99
    assert g.obtener_conexion("a", "b")["peso"] == 2  # lo no indicado se conserva


def test_conexiones_dirigido():
    g = red_pequena(dirigido=True)
    assert g.existe_conexion("a", "b") and not g.existe_conexion("b", "a")
    assert g.vecinos("b") == ["c"] and g.predecesores("b") == ["a"]
    assert (g.grado_entrada("b"), g.grado_salida("b"), g.grado("b")) == (1, 1, 2)
    g.agregar_conexion("b", "a")  # sentido contrario es otra conexión
    assert g.num_conexiones == 3


def test_conexion_invalida():
    g = red_pequena()
    with pytest.raises(ErrorGrafo):
        g.agregar_conexion("a", "a")  # lazo
    with pytest.raises(ErrorGrafo):
        g.agregar_conexion("a", "b")  # repetida
    with pytest.raises(ErrorGrafo):
        g.agregar_conexion("a", "zzz")  # nodo inexistente
    for kwargs in ({"peso": 0}, {"peso": -1}, {"frecuencia": -1}, {"eventos": -1},
                   {"eventos": 1.5}, {"peso": "x"}, {"peso": True}, {"frecuencia": float("nan")},
                   {"peso": float("inf")}):
        with pytest.raises(ErrorGrafo):
            g.agregar_conexion("a", "c", **kwargs)
    assert g.num_conexiones == 2  # ninguna conexión inválida quedó guardada


def test_editar_conexion_invalida_no_modifica():
    g = red_pequena()
    with pytest.raises(ErrorGrafo):
        g.editar_conexion("a", "b", peso=-5)
    assert g.obtener_conexion("a", "b")["peso"] == 2
    with pytest.raises(ErrorGrafo):
        g.editar_conexion("a", "c", peso=1)  # no existe


@pytest.mark.parametrize("dirigido", [False, True])
def test_eliminar_conexion_y_nodo(dirigido):
    g = red_pequena(dirigido)
    g.eliminar_conexion("a", "b")
    assert not g.existe_conexion("a", "b") and g.num_conexiones == 1
    with pytest.raises(ErrorGrafo):
        g.eliminar_conexion("a", "b")
    g = red_pequena(dirigido)
    g.eliminar_nodo("b")
    assert g.nodos() == ["a", "c"] and g.num_conexiones == 0
    assert g.vecinos("a") == [] and g.predecesores("c") == []
    with pytest.raises(ErrorGrafo):
        g.eliminar_nodo("b")


def test_eliminar_nodo_con_entradas_dirigido():
    g = Grafo(True)
    for n in "abc":
        g.agregar_nodo(n)
    g.agregar_conexion("a", "c")
    g.agregar_conexion("b", "c")
    g.agregar_conexion("c", "a")
    g.eliminar_nodo("c")
    assert g.num_conexiones == 0 and g.vecinos("a") == [] and g.vecinos("b") == []


def test_listas_y_matriz():
    g = red_pequena()
    assert g.lista_adyacencia() == {"a": ["b"], "b": ["a", "c"], "c": ["b"]}
    nodos, m = g.matriz_adyacencia()
    assert nodos == ["a", "b", "c"]
    assert m == [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    _, mp = g.matriz_adyacencia(usar_pesos=True)
    assert mp[0][1] == 2 and mp[1][0] == 2
    gd = red_pequena(True)
    _, md = gd.matriz_adyacencia()
    assert md == [[0, 1, 0], [0, 0, 1], [0, 0, 0]]


def test_grafo_vacio_y_total_eventos():
    g = Grafo()
    assert g.num_nodos == 0 and g.num_conexiones == 0 and g.conexiones() == []
    assert g.matriz_adyacencia() == ([], []) and g.total_eventos() == 0
    assert red_pequena().total_eventos() == 5


def test_a_dict_y_copiar_son_independientes():
    g = red_pequena(True)
    c = g.copiar()
    assert c.a_dict() == g.a_dict()
    c.eliminar_nodo("a")
    assert "a" in g and g.num_conexiones == 2


# ---------- Métricas ----------
def test_nodos_por_grado_ordena_y_desempata():
    g = Grafo()
    for n in "abcd":
        g.agregar_nodo(n)
    g.agregar_conexion("a", "b")
    g.agregar_conexion("a", "c")
    g.agregar_conexion("a", "d")
    g.agregar_conexion("b", "c")
    assert nodos_por_grado(g) == [("a", 3), ("b", 2), ("c", 2), ("d", 1)]
    assert nodos_por_grado(g, limite=1) == [("a", 3)]
    assert nodos_por_grado(Grafo()) == []


def test_comparar_representaciones():
    g = red_pequena()
    r = comparar_representaciones(g)
    assert r["celdas_lista"] == 3 + 4 and r["celdas_matriz"] == 9
    assert r["densidad"] == pytest.approx(2 / 3)
    assert comparar_representaciones(Grafo())["densidad"] == 0.0
    assert celdas_representaciones(3, 2, True) == {"lista": 5, "matriz": 9}


def test_crecimiento_representaciones():
    filas = crecimiento_representaciones([10, 100], conexiones_por_nodo=2)
    assert filas[0] == {"nodos": 10, "conexiones": 20, "celdas_lista": 50, "celdas_matriz": 100}
    assert filas[1]["celdas_matriz"] == 10000 and filas[1]["celdas_lista"] == 500
    with pytest.raises(ValueError):
        crecimiento_representaciones([-1])
    with pytest.raises(ValueError):
        crecimiento_representaciones([5], conexiones_por_nodo=-1)
