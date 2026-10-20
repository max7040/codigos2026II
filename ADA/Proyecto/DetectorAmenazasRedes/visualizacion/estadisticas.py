"""Gráficos estadísticos con Plotly (Módulo G).

Cada función recibe datos ya calculados por otros módulos y devuelve una
plotly.graph_objects.Figure. No calculan nada propio: solo presentan.
"""

import plotly.graph_objects as go

from analisis.detector import NIVELES

COLORES_NIVEL = {"Crítico": "#7f0000", "Alto": "#d62728", "Medio": "#ff7f0e", "Bajo": "#f2c744"}
COLORES_ALGORITMO = {"Burbuja": "#d62728", "Inserción": "#ff7f0e", "Selección": "#9467bd",
                     "Merge Sort": "#2ca02c", "Quick Sort": "#1f77b4"}


def _base(figura, titulo, x=None, y=None):
    figura.update_layout(title=titulo, template="plotly_white", height=420,
                         margin=dict(l=10, r=10, t=50, b=10),
                         xaxis_title=x, yaxis_title=y)
    return figura


def grafico_nodos_por_grado(pares):
    """Barras horizontales. pares = [(nodo, grado)] (ver metricas_grafo.nodos_por_grado)."""
    pares = list(reversed(pares))  # el mayor queda arriba
    figura = go.Figure(go.Bar(x=[g for _, g in pares], y=[n for n, _ in pares], orientation="h",
                              marker_color="#1f77b4"))
    return _base(figura, "Nodos con mayor cantidad de conexiones", "Grado", "Nodo")


def grafico_eventos_por_conexion(conexiones, limite=10):
    """Barras con los eventos de las conexiones más activas. conexiones = grafo.conexiones()."""
    ordenadas = sorted(conexiones, key=lambda c: c["eventos"], reverse=True)[:limite]
    ordenadas.reverse()
    etiquetas = [f"{c['origen']} → {c['destino']}" for c in ordenadas]
    figura = go.Figure(go.Bar(x=[c["eventos"] for c in ordenadas], y=etiquetas,
                              orientation="h", marker_color="#ff7f0e"))
    return _base(figura, f"Eventos simulados por conexión (top {limite})", "Eventos", "Conexión")


def grafico_alertas_por_nivel(resumen):
    """Barras por nivel de riesgo. resumen = detector.resumen_por_nivel(alertas)."""
    figura = go.Figure(go.Bar(x=list(NIVELES), y=[resumen.get(n, 0) for n in NIVELES],
                              marker_color=[COLORES_NIVEL[n] for n in NIVELES]))
    return _base(figura, "Alertas por nivel de riesgo", "Nivel", "Cantidad de alertas")


def grafico_comparacion_representaciones(filas):
    """Líneas de celdas usadas por lista y matriz. filas = crecimiento_representaciones(...)."""
    figura = go.Figure()
    figura.add_trace(go.Scatter(x=[f["nodos"] for f in filas], y=[f["celdas_lista"] for f in filas],
                                mode="lines+markers", name="Lista de adyacencia"))
    figura.add_trace(go.Scatter(x=[f["nodos"] for f in filas], y=[f["celdas_matriz"] for f in filas],
                                mode="lines+markers", name="Matriz de adyacencia"))
    return _base(figura, "Crecimiento teórico de las representaciones", "Nodos (n)", "Celdas")


def grafico_benchmark(registros, tipo, escala_log=False):
    """Tiempo promedio vs tamaño para un tipo de datos. registros = ejecutar_benchmark(...)."""
    figura = go.Figure()
    algoritmos = []
    for r in registros:
        if r["algoritmo"] not in algoritmos:
            algoritmos.append(r["algoritmo"])
    for nombre in algoritmos:
        pts = sorted((r["n"], r["promedio_s"]) for r in registros
                     if r["algoritmo"] == nombre and r["tipo"] == tipo)
        figura.add_trace(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts],
                                    mode="lines+markers", name=nombre,
                                    line=dict(color=COLORES_ALGORITMO.get(nombre))))
    _base(figura, f"Tiempo promedio medido — datos «{tipo}»", "Tamaño de entrada (n)", "Segundos")
    if escala_log:
        figura.update_yaxes(type="log")
    return figura
