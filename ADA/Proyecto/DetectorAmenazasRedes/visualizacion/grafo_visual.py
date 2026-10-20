"""Visualización del grafo: NetworkX calcula las posiciones y Plotly dibuja.

Flujo de datos:
  Grafo (propio)  --a_networkx-->  nx.Graph/DiGraph  --calcular_posiciones-->  {nodo: (x, y)}
  posiciones + alertas  --construir_figura-->  plotly.graph_objects.Figure
NetworkX solo se usa para obtener las coordenadas (layouts); el modelo de datos
y las reglas siguen en nuestras propias estructuras.
"""

import networkx as nx
import plotly.graph_objects as go

from estructuras.grafo import TIPOS_NODO

COLORES_TIPO = {"equipo": "#1f77b4", "servidor": "#2ca02c", "cuenta": "#ff7f0e"}
SIMBOLOS_TIPO = {"equipo": "circle", "servidor": "square", "cuenta": "diamond"}
COLOR_ALERTA = "#d62728"
COLOR_ARISTA = "#9aa0a6"
LAYOUTS = ("resorte", "circular", "concéntrico", "aleatorio")


def a_networkx(grafo):
    """Convierte el Grafo propio en un grafo de NetworkX con sus atributos."""
    G = nx.DiGraph() if grafo.dirigido else nx.Graph()
    for nodo in grafo.nodos():
        G.add_node(nodo, tipo=grafo.tipo_nodo(nodo))
    for c in grafo.conexiones():
        G.add_edge(c["origen"], c["destino"], peso=c["peso"],
                   frecuencia=c["frecuencia"], eventos=c["eventos"])
    return G


def calcular_posiciones(G, layout="resorte", semilla=42):
    """Devuelve {nodo: (x, y)} según la distribución elegida."""
    if layout not in LAYOUTS:
        raise ValueError(f"Distribución desconocida: {layout!r}. Opciones: {', '.join(LAYOUTS)}.")
    if len(G) == 0:
        return {}
    if layout == "resorte":
        pos = nx.spring_layout(G, seed=semilla)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "aleatorio":
        pos = nx.random_layout(G, seed=semilla)
    else:  # concéntrico: un anillo por tipo de nodo
        anillos = [[n for n, d in G.nodes(data=True) if d["tipo"] == t] for t in TIPOS_NODO]
        pos = nx.shell_layout(G, nlist=[a for a in anillos if a])
    return {n: (float(x), float(y)) for n, (x, y) in pos.items()}


def _clave_arista(origen, destino, dirigido):
    return (origen, destino) if dirigido else frozenset((origen, destino))


def construir_figura(grafo, alertas=None, layout="resorte", mostrar_pesos=True,
                     semilla=42, titulo="Red simulada"):
    """Construye la figura interactiva de Plotly (nodos por tipo, alertas en rojo)."""
    alertas = alertas or []
    figura = go.Figure()
    figura.update_layout(
        title=titulo, template="plotly_white", height=620, hovermode="closest",
        xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x"),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="left", x=0),
    )
    if grafo.num_nodos == 0:
        figura.add_annotation(text="La red no tiene nodos todavía.", x=0.5, y=0.5,
                              xref="paper", yref="paper", showarrow=False, font=dict(size=16))
        return figura

    G = a_networkx(grafo)
    pos = calcular_posiciones(G, layout, semilla)
    nodos_alerta = {a.objetivo for a in alertas if a.tipo_objetivo == "nodo"}
    aristas_alerta = {_clave_arista(a.objetivo[0], a.objetivo[1], grafo.dirigido)
                      for a in alertas if a.tipo_objetivo == "conexion"}
    alertas_por_nodo, alertas_por_arista = {}, {}
    for a in alertas:
        if a.tipo_objetivo == "nodo":
            alertas_por_nodo.setdefault(a.objetivo, []).append(a.nombre_regla)
        else:
            k = _clave_arista(a.objetivo[0], a.objetivo[1], grafo.dirigido)
            alertas_por_arista.setdefault(k, []).append(a.nombre_regla)

    # --- Aristas (normales y en alerta) ---
    conexiones = grafo.conexiones()
    for en_alerta, color, ancho, nombre in ((False, COLOR_ARISTA, 1.5, "Conexión"),
                                            (True, COLOR_ALERTA, 3.5, "Conexión en alerta")):
        xs, ys = [], []
        for c in conexiones:
            k = _clave_arista(c["origen"], c["destino"], grafo.dirigido)
            if (k in aristas_alerta) == en_alerta:
                (x0, y0), (x1, y1) = pos[c["origen"]], pos[c["destino"]]
                xs += [x0, x1, None]
                ys += [y0, y1, None]
        if xs:
            figura.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=nombre,
                                        line=dict(color=color, width=ancho), hoverinfo="skip"))

    # --- Puntos medios: información al pasar el cursor y etiquetas de peso ---
    mx, my, hover, etiquetas = [], [], [], []
    for c in conexiones:
        (x0, y0), (x1, y1) = pos[c["origen"]], pos[c["destino"]]
        mx.append((x0 + x1) / 2)
        my.append((y0 + y1) / 2)
        k = _clave_arista(c["origen"], c["destino"], grafo.dirigido)
        flecha = "→" if grafo.dirigido else "—"
        texto = (f"<b>{c['origen']} {flecha} {c['destino']}</b><br>Peso: {c['peso']:g}"
                 f"<br>Frecuencia: {c['frecuencia']:g}<br>Eventos: {c['eventos']}")
        if k in alertas_por_arista:
            texto += "<br><b>Alertas:</b> " + "; ".join(alertas_por_arista[k])
        hover.append(texto)
        etiquetas.append(f"{c['peso']:g}")
    if mx:
        figura.add_trace(go.Scatter(
            x=mx, y=my, mode="markers+text" if mostrar_pesos else "markers",
            text=etiquetas if mostrar_pesos else None, textposition="top center",
            textfont=dict(size=10, color="#555"), marker=dict(size=14, opacity=0),
            hovertext=hover, hoverinfo="text", showlegend=False, name="Detalle de conexión"))

    # --- Flechas (solo grafos dirigidos) ---
    if grafo.dirigido:
        for c in conexiones:
            (x0, y0), (x1, y1) = pos[c["origen"]], pos[c["destino"]]
            k = _clave_arista(c["origen"], c["destino"], True)
            figura.add_annotation(
                x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=1.5, standoff=16,
                arrowcolor=COLOR_ALERTA if k in aristas_alerta else COLOR_ARISTA, text="")

    # --- Nodos, un trazo por tipo (cada tipo aparece en la leyenda) ---
    for tipo in TIPOS_NODO:
        nodos_tipo = [n for n in grafo.nodos() if grafo.tipo_nodo(n) == tipo]
        if not nodos_tipo:
            continue
        hover = []
        for n in nodos_tipo:
            texto = f"<b>{n}</b><br>Tipo: {tipo}<br>Grado: {grafo.grado(n)}"
            if grafo.dirigido:
                texto += f" (entrada {grafo.grado_entrada(n)}, salida {grafo.grado_salida(n)})"
            if n in alertas_por_nodo:
                texto += "<br><b>Alertas:</b> " + "; ".join(alertas_por_nodo[n])
            hover.append(texto)
        figura.add_trace(go.Scatter(
            x=[pos[n][0] for n in nodos_tipo], y=[pos[n][1] for n in nodos_tipo],
            mode="markers+text", name=tipo.capitalize(), text=nodos_tipo,
            textposition="bottom center", hovertext=hover, hoverinfo="text",
            marker=dict(
                size=[18 + 2 * min(grafo.grado(n), 8) for n in nodos_tipo],
                color=COLORES_TIPO[tipo], symbol=SIMBOLOS_TIPO[tipo],
                line=dict(color=[COLOR_ALERTA if n in nodos_alerta else "#333" for n in nodos_tipo],
                          width=[4 if n in nodos_alerta else 1 for n in nodos_tipo]))))

    # --- Entrada de leyenda para nodos en alerta ---
    if nodos_alerta:
        figura.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers", name="Nodo en alerta (borde rojo)",
            marker=dict(size=14, color="white", line=dict(color=COLOR_ALERTA, width=4))))
    return figura
