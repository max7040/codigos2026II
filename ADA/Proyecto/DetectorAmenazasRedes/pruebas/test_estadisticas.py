"""Pruebas básicas de los gráficos estadísticos (Módulo G)."""

import plotly.graph_objects as go

from analisis.benchmark import ejecutar_benchmark
from analisis.detector import NIVELES
from analisis.metricas_grafo import crecimiento_representaciones
from visualizacion import estadisticas as g


def test_alertas_por_nivel_tiene_una_barra_por_nivel():
    fig = g.grafico_alertas_por_nivel({n: 1 for n in NIVELES})
    assert isinstance(fig, go.Figure)
    assert list(fig.data[0].x) == list(NIVELES)


def test_nodos_por_grado_mantiene_los_valores():
    fig = g.grafico_nodos_por_grado([("a", 3), ("b", 1)])
    assert sorted(fig.data[0].x) == [1, 3]


def test_representaciones_dos_series():
    fig = g.grafico_comparacion_representaciones(crecimiento_representaciones([10, 20]))
    assert len(fig.data) == 2


def test_benchmark_una_serie_por_algoritmo():
    registros = ejecutar_benchmark(nombres=["Burbuja", "Merge Sort"], tamanos=(10, 20), repeticiones=1)
    fig = g.grafico_benchmark(registros, "aleatorio")
    assert len(fig.data) == 2


def test_eventos_por_conexion_respeta_el_limite():
    conexiones = [{"origen": "a", "destino": str(i), "eventos": i} for i in range(20)]
    fig = g.grafico_eventos_por_conexion(conexiones, limite=5)
    assert len(fig.data[0].x) == 5
