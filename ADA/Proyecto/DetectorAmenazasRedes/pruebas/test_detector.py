"""Pruebas del detector de amenazas simuladas."""

from pathlib import Path

import pytest

from analisis.detector import (
    NIVELES,
    ConfigDetector,
    calcular_riesgo,
    conexiones_con_alerta,
    detectar,
    nodos_con_alerta,
    resumen_por_nivel,
)
from estructuras.grafo import Grafo
from utils.validaciones import importar_json

EJEMPLO = Path(__file__).resolve().parent.parent / "data" / "ejemplo_red.json"


def estrella(n_hojas, dirigido=False):
    g = Grafo(dirigido)
    g.agregar_nodo("hub", "servidor")
    for i in range(n_hojas):
        g.agregar_nodo(f"h{i}", "equipo")
        g.agregar_conexion(f"h{i}", "hub")
    return g


@pytest.mark.parametrize("valor,puntaje,nivel", [
    (5, 50, "Bajo"), (6, 60, "Medio"), (8, 80, "Alto"), (10, 100, "Crítico"), (50, 100, "Crítico"),
])
def test_calcular_riesgo_con_umbral_5(valor, puntaje, nivel):
    assert calcular_riesgo(valor, 5) == (puntaje, nivel)


def test_calcular_riesgo_umbral_invalido():
    with pytest.raises(ValueError):
        calcular_riesgo(1, 0)


def test_regla_grado_alto_en_el_umbral_y_debajo():
    assert detectar(estrella(4)) == []  # grado del hub = 4 < 5
    alertas = detectar(estrella(5))
    assert len(alertas) == 1
    a = alertas[0]
    assert (a.regla, a.objetivo, a.valor, a.umbral) == ("GRADO_ALTO", "hub", 5, 5)
    assert (a.puntaje, a.nivel) == (50, "Bajo")
    assert a.datos["grado"] == 5 and len(a.datos["vecinos"]) == 5
    assert a.recomendacion and "umbral" in a.explicacion


def test_grado_alto_dirigido_incluye_entrada_y_salida():
    a = detectar(estrella(5, dirigido=True))[0]
    assert a.datos["grado_entrada"] == 5 and a.datos["grado_salida"] == 0


def test_reglas_de_conexion():
    g = Grafo(True)
    for n in ("x", "y"):
        g.agregar_nodo(n)
    g.agregar_conexion("x", "y", frecuencia=150, eventos=60)
    alertas = detectar(g)
    reglas = {a.regla: a for a in alertas}
    assert set(reglas) == {"FRECUENCIA_ALTA", "EVENTOS_REPETIDOS"}
    assert reglas["FRECUENCIA_ALTA"].puntaje == 75 and reglas["FRECUENCIA_ALTA"].nivel == "Medio"
    assert reglas["EVENTOS_REPETIDOS"].puntaje == 60
    assert conexiones_con_alerta(alertas) == {("x", "y")} and nodos_con_alerta(alertas) == set()
    assert reglas["FRECUENCIA_ALTA"].descripcion_objetivo == "x -> y"


def test_regla_cuenta_multi_servidor_solo_aplica_a_cuentas():
    g = Grafo(True)
    g.agregar_nodo("cta", "cuenta")
    g.agregar_nodo("pc", "equipo")
    for i in range(3):
        g.agregar_nodo(f"s{i}", "servidor")
        g.agregar_conexion("cta", f"s{i}")
        g.agregar_conexion("pc", f"s{i}")
    alertas = detectar(g, ConfigDetector(umbral_grado=100))
    assert len(alertas) == 1
    assert alertas[0].objetivo == "cta" and sorted(alertas[0].datos["servidores"]) == ["s0", "s1", "s2"]


def test_config_reglas_activas_y_umbrales():
    g = estrella(5)
    assert detectar(g, ConfigDetector(reglas_activas=frozenset({"FRECUENCIA_ALTA"}))) == []
    assert detectar(g, ConfigDetector(reglas_activas=frozenset())) == []
    assert detectar(g, ConfigDetector(umbral_grado=10)) == []
    assert detectar(g, ConfigDetector(umbral_grado=2))[0].puntaje == 100  # 5/2 -> tope 100


@pytest.mark.parametrize("kwargs", [{"umbral_grado": 0}, {"umbral_frecuencia": -1},
                                    {"umbral_eventos": "x"}, {"umbral_servidores": True},
                                    {"reglas_activas": frozenset({"INVENTADA"})}])
def test_config_invalida(kwargs):
    with pytest.raises(ValueError):
        detectar(Grafo(), ConfigDetector(**kwargs))


def test_grafo_vacio_sin_alertas():
    assert detectar(Grafo()) == [] and resumen_por_nivel([]) == {n: 0 for n in NIVELES}


def test_ejemplo_del_proyecto_resultados_esperados():
    """Resultados calculados a mano a partir de data/ejemplo_red.json y las reglas por defecto."""
    g = importar_json(EJEMPLO.read_text(encoding="utf-8"))
    alertas = detectar(g)
    clave = {(a.regla, a.descripcion_objetivo): (a.puntaje, a.nivel) for a in alertas}
    assert clave == {
        ("EVENTOS_REPETIDOS", "pc-03 -> srv-web"): (100, "Crítico"),
        ("EVENTOS_REPETIDOS", "cta-invitado -> srv-archivos"): (75, "Medio"),
        ("FRECUENCIA_ALTA", "pc-03 -> srv-web"): (90, "Alto"),
        ("GRADO_ALTO", "srv-web"): (90, "Alto"),      # grado 9 = 7 entradas + 2 salidas -> 9/5 -> 90
        ("GRADO_ALTO", "cta-admin"): (50, "Bajo"),
        ("CUENTA_MULTI_SERVIDOR", "cta-admin"): (67, "Medio"),
    }
    puntajes = [a.puntaje for a in alertas]
    assert puntajes == sorted(puntajes, reverse=True)  # orden por riesgo
    assert [a.id_alerta for a in alertas] == [f"A{i:03d}" for i in range(1, len(alertas) + 1)]
    assert resumen_por_nivel(alertas) == {"Crítico": 1, "Alto": 2, "Medio": 2, "Bajo": 1}
