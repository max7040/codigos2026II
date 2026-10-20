"""Pruebas de la Fase 1: algoritmos, estructuras y benchmark."""

import itertools
import random

import pytest

from algoritmos.busqueda import busqueda_binaria, busqueda_binaria_recursiva, busqueda_lineal
from algoritmos.divide_conquista import merge_sort, quick_sort
from algoritmos.ordenamiento import burbuja, insercion, seleccion
from algoritmos.programacion_dinamica import cadena_matrices, mochila_01
from algoritmos.recursion import (
    LIMITE_FIBONACCI_RECURSIVO,
    factorial_iterativo,
    factorial_recursivo,
    fibonacci_iterativo,
    fibonacci_memoizado,
    fibonacci_recursivo,
    fibonacci_tabulacion,
)
from algoritmos.voraces import mochila_fraccionaria, seleccion_actividades
from analisis.benchmark import (
    ALGORITMOS,
    ejecutar_benchmark,
    generar_datos,
    medir,
)
from estructuras.arbol_binario import ArbolBinarioBusqueda
from estructuras.tabla_hash import TablaHash

ORDENADORES = [burbuja, insercion, seleccion, merge_sort, quick_sort]
CASOS = [
    [],
    [1],
    [2, 1],
    [3, 3, 3],
    [5, 1, 4, 2, 8, 1, 5],
    [1, 2, 3, 4, 5],
    [5, 4, 3, 2, 1],
    [-3, 0, -1, 7, 7, -3],
]


# ---------- Ordenamiento ----------
@pytest.mark.parametrize("algoritmo", ORDENADORES)
@pytest.mark.parametrize("caso", CASOS)
def test_ordenamiento_casos(algoritmo, caso):
    original = list(caso)
    assert algoritmo(caso) == sorted(caso)
    assert caso == original  # no modifica la entrada


@pytest.mark.parametrize("algoritmo", ORDENADORES)
def test_ordenamiento_aleatorio(algoritmo):
    rng = random.Random(1)
    for _ in range(20):
        datos = [rng.randint(-50, 50) for _ in range(rng.randint(0, 60))]
        assert algoritmo(datos) == sorted(datos)


def test_quick_sort_grande_ordenado_e_inverso():
    assert quick_sort(list(range(3000))) == list(range(3000))
    assert quick_sort(list(range(3000, 0, -1))) == list(range(1, 3001))


def test_ordenamiento_con_tuplas():
    datos = [(1, "a"), (0, "b"), (1, "c"), (0, "d")]
    assert merge_sort(datos) == sorted(datos)
    assert quick_sort(datos) == sorted(datos)


# ---------- Búsqueda ----------
def test_busqueda_lineal():
    datos = [4, 2, 9, 2]
    assert busqueda_lineal(datos, 9) == 2
    assert busqueda_lineal(datos, 2) == 1  # primera aparición
    assert busqueda_lineal(datos, 7) == -1
    assert busqueda_lineal([], 1) == -1


@pytest.mark.parametrize("buscar", [busqueda_binaria, busqueda_binaria_recursiva])
def test_busqueda_binaria(buscar):
    datos = [1, 3, 5, 7, 9, 11]
    for i, valor in enumerate(datos):
        assert buscar(datos, valor) == i
    assert buscar(datos, 0) == -1
    assert buscar(datos, 12) == -1
    assert buscar(datos, 6) == -1
    assert buscar([], 1) == -1
    assert buscar([5], 5) == 0
    assert buscar([2, 2, 2, 2], 2) in range(4)  # repetidos


# ---------- Recursión ----------
def test_factorial():
    for n, esperado in [(0, 1), (1, 1), (5, 120), (10, 3628800)]:
        assert factorial_recursivo(n) == esperado
        assert factorial_iterativo(n) == esperado
    with pytest.raises(ValueError):
        factorial_recursivo(-1)
    with pytest.raises(ValueError):
        factorial_iterativo(-1)


def test_fibonacci_enfoques_coinciden():
    conocidos = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    for n, esperado in enumerate(conocidos):
        assert fibonacci_recursivo(n) == esperado
        assert fibonacci_iterativo(n) == esperado
        assert fibonacci_memoizado(n) == esperado
        assert fibonacci_tabulacion(n) == esperado
    assert fibonacci_iterativo(90) == fibonacci_tabulacion(90) == fibonacci_memoizado(90)
    assert fibonacci_iterativo(90) == 2880067194370816120


def test_fibonacci_limites():
    with pytest.raises(ValueError):
        fibonacci_recursivo(LIMITE_FIBONACCI_RECURSIVO + 1)
    for f in (fibonacci_recursivo, fibonacci_iterativo, fibonacci_memoizado, fibonacci_tabulacion):
        with pytest.raises(ValueError):
            f(-1)


# ---------- Tabla hash ----------
def test_tabla_hash_basica():
    t = TablaHash()
    t.insertar("a", 1)
    t.insertar("b", 2)
    assert t.buscar("a") == 1
    assert t.buscar("z") is None
    assert t.buscar("z", "nada") == "nada"
    assert "b" in t and "z" not in t
    t.insertar("a", 10)  # actualiza
    assert t.buscar("a") == 10 and len(t) == 2
    assert t.eliminar("a") is True
    assert t.eliminar("a") is False
    assert len(t) == 1


def test_tabla_hash_colisiones():
    t = TablaHash(capacidad=8)
    t.insertar(1, "uno")
    t.insertar(9, "nueve")  # 1 % 8 == 9 % 8 -> colisión
    assert t.estadisticas()["cadena_maxima"] == 2
    assert t.buscar(1) == "uno" and t.buscar(9) == "nueve"
    assert t.eliminar(1) is True
    assert t.buscar(9) == "nueve"


def test_tabla_hash_redimensiona_y_conserva():
    t = TablaHash(capacidad=2)
    for i in range(200):
        t.insertar(f"clave{i}", i)
    assert len(t) == 200
    assert t.capacidad > 2
    assert all(t.buscar(f"clave{i}") == i for i in range(200))
    assert t.estadisticas()["factor_carga"] <= TablaHash.FACTOR_CARGA_MAXIMO


def test_tabla_hash_capacidad_invalida():
    with pytest.raises(ValueError):
        TablaHash(0)


# ---------- Árbol binario de búsqueda ----------
def test_arbol_insertar_buscar():
    a = ArbolBinarioBusqueda()
    assert len(a) == 0 and a.altura() == 0 and a.minimo() is None
    assert not a.buscar(1) and a.inorden() == []
    for x in [50, 30, 70, 20, 40, 60, 80]:
        assert a.insertar(x) is True
    assert a.insertar(50) is False  # duplicado
    assert len(a) == 7 and a.altura() == 3
    assert a.inorden() == [20, 30, 40, 50, 60, 70, 80]
    assert 60 in a and 65 not in a
    assert a.minimo() == 20 and a.maximo() == 80


def test_arbol_eliminar_todos_los_casos():
    def construir():
        a = ArbolBinarioBusqueda()
        for x in [50, 30, 70, 20, 40, 60, 80]:
            a.insertar(x)
        return a

    a = construir()
    assert a.eliminar(20) is True  # hoja
    assert a.inorden() == [30, 40, 50, 60, 70, 80]
    a = construir()
    a.eliminar(30)
    a.eliminar(20)  # nodo con un hijo (tras borrar 30 queda 40 con hijo 20)
    assert a.inorden() == [40, 50, 60, 70, 80]
    a = construir()
    assert a.eliminar(50) is True  # raíz con dos hijos
    assert a.inorden() == [20, 30, 40, 60, 70, 80]
    assert a.eliminar(99) is False
    assert len(a) == 6


def test_arbol_degenerado_no_desborda_pila():
    a = ArbolBinarioBusqueda()
    for x in range(3000):
        a.insertar(x)
    assert a.altura() == 3000
    assert a.buscar(2999)
    assert a.inorden() == list(range(3000))


# ---------- Voraces ----------
def test_mochila_fraccionaria():
    # Ejemplo clásico: capacidad 50 -> valor 240
    elementos = [("A", 60, 10), ("B", 100, 20), ("C", 120, 30)]
    total, tomados = mochila_fraccionaria(elementos, 50)
    assert total == pytest.approx(240.0)
    assert dict(tomados) == {"A": 1.0, "B": 1.0, "C": pytest.approx(2 / 3)}


def test_mochila_fraccionaria_bordes():
    assert mochila_fraccionaria([], 10) == (0.0, [])
    assert mochila_fraccionaria([("A", 5, 2)], 0)[0] == 0.0
    assert mochila_fraccionaria([("A", 5, 2)], 100)[0] == 5.0  # cabe completo
    with pytest.raises(ValueError):
        mochila_fraccionaria([("A", 5, 0)], 10)
    with pytest.raises(ValueError):
        mochila_fraccionaria([("A", 5, 1)], -1)


def test_seleccion_actividades():
    acts = [("a1", 1, 4), ("a2", 3, 5), ("a3", 0, 6), ("a4", 5, 7),
            ("a5", 3, 9), ("a6", 5, 9), ("a7", 6, 10), ("a8", 8, 11),
            ("a9", 8, 12), ("a10", 2, 14), ("a11", 12, 16)]
    nombres = [n for n, _, _ in seleccion_actividades(acts)]
    assert nombres == ["a1", "a4", "a8", "a11"]
    assert seleccion_actividades([]) == []
    assert len(seleccion_actividades([("x", 0, 5)])) == 1
    with pytest.raises(ValueError):
        seleccion_actividades([("mala", 5, 1)])


def test_seleccion_actividades_es_optima_vs_fuerza_bruta():
    rng = random.Random(7)
    for _ in range(30):
        acts = []
        for i in range(rng.randint(0, 8)):
            ini = rng.randint(0, 10)
            acts.append((f"x{i}", ini, ini + rng.randint(0, 5)))
        mejor = 0
        for r in range(len(acts) + 1):
            for sub in itertools.combinations(acts, r):
                ordenado = sorted(sub, key=lambda t: (t[2], t[1]))
                if all(ordenado[k + 1][1] >= ordenado[k][2] for k in range(len(ordenado) - 1)):
                    mejor = max(mejor, r)
        assert len(seleccion_actividades(acts)) == mejor


# ---------- Programación dinámica ----------
def test_mochila_01_ejemplo():
    elementos = [("A", 60, 10), ("B", 100, 20), ("C", 120, 30)]
    valor, elegidos = mochila_01(elementos, 50)
    assert valor == 220 and elegidos == ["B", "C"]


def test_mochila_01_bordes():
    assert mochila_01([], 10) == (0, [])
    assert mochila_01([("A", 5, 3)], 2) == (0, [])
    assert mochila_01([("A", 5, 3)], 0) == (0, [])
    assert mochila_01([("A", 5, 0)], 0) == (5, ["A"])
    with pytest.raises(ValueError):
        mochila_01([("A", 5, 1.5)], 3)
    with pytest.raises(ValueError):
        mochila_01([("A", 5, 1)], -1)


def test_mochila_01_vs_fuerza_bruta():
    rng = random.Random(3)
    for _ in range(30):
        elems = [(f"e{i}", rng.randint(0, 20), rng.randint(0, 8)) for i in range(rng.randint(0, 7))]
        cap = rng.randint(0, 20)
        mejor = 0
        for r in range(len(elems) + 1):
            for sub in itertools.combinations(elems, r):
                if sum(e[2] for e in sub) <= cap:
                    mejor = max(mejor, sum(e[1] for e in sub))
        valor, elegidos = mochila_01(elems, cap)
        assert valor == mejor
        por_nombre = {e[0]: e for e in elems}
        assert sum(por_nombre[n][2] for n in elegidos) <= cap
        assert sum(por_nombre[n][1] for n in elegidos) == valor


def test_cadena_matrices():
    assert cadena_matrices([10, 30, 5, 60]) == (4500, "((A1A2)A3)")
    # Ejemplo de CLRS: 30x35, 35x15, 15x5, 5x10, 10x20, 20x25 -> 15125
    assert cadena_matrices([30, 35, 15, 5, 10, 20, 25])[0] == 15125
    assert cadena_matrices([4, 5]) == (0, "A1")
    assert cadena_matrices([2, 3, 4])[0] == 24
    with pytest.raises(ValueError):
        cadena_matrices([5])
    with pytest.raises(ValueError):
        cadena_matrices([5, 0, 3])


# ---------- Benchmark ----------
def test_generar_datos_reproducible_y_tipos():
    assert generar_datos(50, "aleatorio", 1) == generar_datos(50, "aleatorio", 1)
    assert generar_datos(50, "aleatorio", 1) != generar_datos(50, "aleatorio", 2)
    assert generar_datos(5, "ordenado") == [0, 1, 2, 3, 4]
    assert generar_datos(5, "inverso") == [5, 4, 3, 2, 1]
    assert len(generar_datos(0)) == 0
    with pytest.raises(ValueError):
        generar_datos(5, "raro")
    with pytest.raises(ValueError):
        generar_datos(-1)


def test_medir_no_modifica_datos_y_verifica():
    datos = generar_datos(100)
    copia = list(datos)
    tiempos, correcto = medir(merge_sort, datos, repeticiones=3)
    assert datos == copia and len(tiempos) == 3 and correcto
    assert all(t >= 0 for t in tiempos)
    _, correcto = medir(lambda x: x, [3, 1, 2], repeticiones=1)  # algoritmo incorrecto
    assert correcto is False
    with pytest.raises(ValueError):
        medir(merge_sort, datos, repeticiones=0)


def test_benchmark_resultados_correctos():
    registros = ejecutar_benchmark(tamanos=(0, 1, 50, 200),
                                   tipos=("aleatorio", "ordenado", "inverso", "con_repetidos"),
                                   repeticiones=2)
    assert len(registros) == 4 * 4 * len(ALGORITMOS)
    assert all(r["correcto"] for r in registros)
    assert all(r["mejor_s"] <= r["promedio_s"] <= r["peor_s"] for r in registros)


def test_benchmark_algoritmo_desconocido():
    with pytest.raises(ValueError):
        ejecutar_benchmark(nombres=["Inexistente"])
