"""Pruebas de importación/exportación y validación de redes."""

import json
from pathlib import Path

import pytest

from utils.validaciones import (
    ErrorValidacion,
    exportar_csv,
    exportar_json,
    importar_csv,
    importar_json,
    red_desde_dict,
)

EJEMPLO = Path(__file__).resolve().parent.parent / "data" / "ejemplo_red.json"


def test_importar_ejemplo_del_proyecto():
    g = importar_json(EJEMPLO.read_text(encoding="utf-8"))
    assert g.dirigido and g.num_nodos == 12 and g.num_conexiones == 18


def test_json_ida_y_vuelta():
    g = importar_json(EJEMPLO.read_text(encoding="utf-8"))
    g2 = importar_json(exportar_json(g))
    assert g2.a_dict() == g.a_dict()


def test_json_minimo_con_valores_por_defecto():
    g = red_desde_dict({"nodos": [{"id": "a", "tipo": "equipo"}, {"id": "b", "tipo": "servidor"}],
                        "conexiones": [{"origen": "a", "destino": "b"}]})
    assert not g.dirigido
    assert g.obtener_conexion("a", "b") == {"peso": 1.0, "frecuencia": 0.0, "eventos": 0}


@pytest.mark.parametrize("texto", ["", "   ", "{", "esto no es json", "[1, 2]", "null", "123"])
def test_json_malformado_se_rechaza_de_forma_controlada(texto):
    with pytest.raises(ErrorValidacion) as e:
        importar_json(texto)
    assert e.value.errores  # mensaje comprensible, no una excepción cruda


def test_json_acumula_todos_los_errores():
    datos = {
        "dirigido": "si",
        "nodos": [{"id": "a", "tipo": "equipo"}, {"id": "a", "tipo": "equipo"},
                  {"id": "", "tipo": "equipo"}, {"id": "b", "tipo": "router"}, "texto"],
        "conexiones": [{"origen": "a", "destino": "zzz"}, {"origen": "a", "destino": "a"},
                       {"origen": "a", "destino": "b", "peso": -1}, 7],
    }
    with pytest.raises(ErrorValidacion) as e:
        red_desde_dict(datos)
    errores = e.value.errores
    assert len(errores) >= 8
    assert any("dirigido" in x for x in errores)
    assert any("ya existe" in x for x in errores)
    assert any("Nodo #5" in x for x in errores)
    assert any("Conexión #4" in x for x in errores)


def test_json_sin_lista_de_nodos():
    with pytest.raises(ErrorValidacion) as e:
        red_desde_dict({"conexiones": []})
    assert any("nodos" in x for x in e.value.errores)


def test_json_conexion_repetida():
    datos = {"nodos": [{"id": "a", "tipo": "equipo"}, {"id": "b", "tipo": "equipo"}],
             "conexiones": [{"origen": "a", "destino": "b"}, {"origen": "b", "destino": "a"}]}
    with pytest.raises(ErrorValidacion):
        red_desde_dict(datos)  # en no dirigido b-a repite a-b


NODOS_CSV = "id,tipo\na,equipo\nb,servidor\nc,cuenta\n"
CON_CSV = "origen,destino,peso,frecuencia,eventos\na,b,2,10,5\nb,c,,,\n"


def test_csv_ida_y_vuelta():
    g = importar_csv(NODOS_CSV, CON_CSV, dirigido=True)
    assert g.num_nodos == 3 and g.obtener_conexion("a", "b") == {"peso": 2.0, "frecuencia": 10.0, "eventos": 5}
    assert g.obtener_conexion("b", "c")["peso"] == 1.0  # celdas vacías -> valor por defecto
    n_csv, c_csv = exportar_csv(g)
    g2 = importar_csv(n_csv, c_csv, dirigido=True)
    assert g2.a_dict() == g.a_dict()


def test_csv_tolera_espacios_mayusculas_y_filas_vacias():
    nodos = "ID , Tipo\n a , Equipo \n\n b , SERVIDOR\n"
    con = "Origen,Destino\n a , b \n"
    g = importar_csv(nodos, con)
    assert g.nodos() == ["a", "b"] and g.existe_conexion("a", "b")


def test_csv_errores_con_numero_de_fila():
    nodos = "id,tipo\na,equipo\nb,router\nc,equipo\n"
    con = "origen,destino,peso,eventos\na,c,abc,1\na,a,1,1\na,c,1,2.5\n"
    with pytest.raises(ErrorValidacion) as e:
        importar_csv(nodos, con)
    errores = e.value.errores
    assert any("Nodos, fila 3" in x for x in errores)
    assert any("Conexiones, fila 2" in x and "número" in x for x in errores)
    assert any("Conexiones, fila 3" in x for x in errores)
    assert any("Conexiones, fila 4" in x and "entero" in x for x in errores)


def test_csv_columnas_faltantes_o_vacio():
    with pytest.raises(ErrorValidacion) as e:
        importar_csv("nombre,tipo\na,equipo\n", "origen\na\n")
    assert len(e.value.errores) == 2
    with pytest.raises(ErrorValidacion):
        importar_csv("", "")


def test_exportar_json_conserva_acentos_y_es_json_valido():
    g = red_desde_dict({"nodos": [{"id": "ñandú", "tipo": "equipo"}]})
    texto = exportar_json(g)
    assert "ñandú" in texto and json.loads(texto)["nodos"][0]["id"] == "ñandú"
