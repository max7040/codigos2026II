"""Pruebas de la visualización (NetworkX + Plotly). No se abre ninguna ventana."""

from pathlib import Path

import networkx as nx
import plotly.graph_objects as go
import pytest

from analisis.detector import detectar
from estructuras.grafo import Grafo
from utils.validaciones import importar_json
from visualizacion.grafo_visual import (
    COLOR_ALERTA,
    LAYOUTS,
    a_networkx,
    calcular_posiciones,
    construir_figura,
)

EJEMPLO = Path(__file__).resolve().parent.parent / "data" / "ejemplo_red.json"


@pytest.fixture
def red():
    return importar_json(EJEMPLO.read_text(encoding="utf-8"))


def nombres(fig):
    return [t.name for t in fig.data]


def test_a_networkx_conserva_estructura_y_atributos(red):
    G = a_networkx(red)
    assert isinstance(G, nx.DiGraph)
    assert G.number_of_nodes() == red.num_nodos and G.number_of_edges() == red.num_conexiones
    assert G.nodes["srv-web"]["tipo"] == "servidor"
    assert G["pc-03"]["srv-web"]["eventos"] == 300
    g = Grafo()
    g.agregar_nodo("a")
    g.agregar_nodo("b")
    g.agregar_conexion("a", "b")
    assert not isinstance(a_networkx(g), nx.DiGraph)


@pytest.mark.parametrize("layout", LAYOUTS)
def test_posiciones_para_cada_distribucion(red, layout):
    pos = calcular_posiciones(a_networkx(red), layout)
    assert set(pos) == set(red.nodos())
    assert all(len(p) == 2 for p in pos.values())


def test_posiciones_reproducibles_y_casos_limite(red):
    G = a_networkx(red)
    assert calcular_posiciones(G, "resorte", 7) == calcular_posiciones(G, "resorte", 7)
    assert calcular_posiciones(nx.Graph()) == {}
    g = Grafo()
    g.agregar_nodo("solo")
    for layout in LAYOUTS:
        assert set(calcular_posiciones(a_networkx(g), layout)) == {"solo"}
    with pytest.raises(ValueError):
        calcular_posiciones(G, "inexistente")


def test_figura_sin_alertas(red):
    fig = construir_figura(red)
    assert isinstance(fig, go.Figure)
    assert {"Equipo", "Servidor", "Cuenta", "Conexión"} <= set(nombres(fig))
    assert "Conexión en alerta" not in nombres(fig)
    assert len(fig.layout.annotations) == red.num_conexiones  # una flecha por conexión dirigida


def test_figura_resalta_alertas_en_rojo(red):
    alertas = detectar(red)
    fig = construir_figura(red, alertas)
    assert "Conexión en alerta" in nombres(fig) and "Nodo en alerta (borde rojo)" in nombres(fig)
    traza_alerta = next(t for t in fig.data if t.name == "Conexión en alerta")
    assert traza_alerta.line.color == COLOR_ALERTA
    # Hay 2 conexiones en alerta (pc-03 -> srv-web y cta-invitado -> srv-archivos);
    # cada segmento ocupa 3 puntos (x0, x1, None).
    assert len(traza_alerta.x) == 6
    servidores = next(t for t in fig.data if t.name == "Servidor")
    i = list(servidores.text).index("srv-web")
    assert servidores.marker.line.color[i] == COLOR_ALERTA
    assert "Alertas" in servidores.hovertext[i]
    otros = [c for j, c in enumerate(servidores.marker.line.color) if j != i]
    assert COLOR_ALERTA not in otros  # solo srv-web tiene alerta de nodo entre los servidores


def test_hover_de_conexion_y_pesos(red):
    fig = construir_figura(red, mostrar_pesos=True)
    detalle = next(t for t in fig.data if t.name == "Detalle de conexión")
    assert "text" in detalle.mode and len(detalle.hovertext) == red.num_conexiones
    assert any("pc-03" in h and "Eventos: 300" in h for h in detalle.hovertext)
    fig2 = construir_figura(red, mostrar_pesos=False)
    assert "text" not in next(t for t in fig2.data if t.name == "Detalle de conexión").mode


def test_grafo_no_dirigido_sin_flechas():
    g = Grafo()
    for n in "abc":
        g.agregar_nodo(n, "equipo")
    g.agregar_conexion("a", "b")
    g.agregar_conexion("b", "c")
    fig = construir_figura(g)
    assert len(fig.layout.annotations) == 0 and nombres(fig).count("Equipo") == 1


def test_alerta_en_no_dirigido_se_resalta_en_cualquier_sentido():
    g = Grafo()
    g.agregar_nodo("a")
    g.agregar_nodo("b")
    g.agregar_conexion("a", "b", eventos=100)
    alertas = detectar(g)
    assert "Conexión en alerta" in nombres(construir_figura(g, alertas))


def test_figura_de_grafo_vacio_y_layout_invalido(red):
    fig = construir_figura(Grafo())
    assert len(fig.data) == 0 and "no tiene nodos" in fig.layout.annotations[0].text
    with pytest.raises(ValueError):
        construir_figura(red, layout="raro")


def test_figura_se_serializa_a_json(red):
    assert construir_figura(red, detectar(red)).to_json()
