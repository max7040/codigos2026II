"""Importación, exportación y validación de redes (JSON y CSV).

Todas las funciones de importación acumulan TODOS los errores encontrados y los
devuelven juntos en un ErrorValidacion, con mensajes comprensibles que indican
la posición del problema (nodo #, conexión #, fila de CSV).

Formato JSON:
{
  "dirigido": true,
  "nodos": [{"id": "srv-web", "tipo": "servidor"}],
  "conexiones": [{"origen": "pc-01", "destino": "srv-web",
                  "peso": 1, "frecuencia": 30, "eventos": 12}]
}
CSV de nodos: columnas id,tipo.
CSV de conexiones: columnas origen,destino y opcionales peso,frecuencia,eventos.
"""

import csv
import io
import json
import math

from estructuras.grafo import ErrorGrafo, Grafo

COLUMNAS_NODOS = ("id", "tipo")
COLUMNAS_CONEXIONES = ("origen", "destino", "peso", "frecuencia", "eventos")
OBLIGATORIAS_CONEXIONES = ("origen", "destino")
VALORES_POR_DEFECTO = {"peso": 1.0, "frecuencia": 0.0, "eventos": 0}


class ErrorValidacion(ValueError):
    """Error de importación con la lista completa de problemas en `errores`."""

    def __init__(self, errores):
        self.errores = list(errores)
        super().__init__("; ".join(self.errores))


def _construir(dirigido, nodos, conexiones, errores):
    """Construye el grafo elemento por elemento, acumulando errores en `errores`."""
    grafo = Grafo(dirigido)
    for i, nodo in enumerate(nodos, start=1):
        etiqueta = nodo.get("_etiqueta", f"Nodo #{i}")
        try:
            grafo.agregar_nodo(nodo.get("id"), nodo.get("tipo"))
        except ErrorGrafo as e:
            errores.append(f"{etiqueta}: {e}")
    for i, c in enumerate(conexiones, start=1):
        etiqueta = c.get("_etiqueta", f"Conexión #{i}")
        try:
            grafo.agregar_conexion(
                _texto_o_none(c.get("origen")),
                _texto_o_none(c.get("destino")),
                c.get("peso", VALORES_POR_DEFECTO["peso"]),
                c.get("frecuencia", VALORES_POR_DEFECTO["frecuencia"]),
                c.get("eventos", VALORES_POR_DEFECTO["eventos"]),
            )
        except ErrorGrafo as e:
            errores.append(f"{etiqueta}: {e}")
    return grafo


def _texto_o_none(valor):
    return valor.strip() if isinstance(valor, str) else valor


# ---------------------------------------------------------------- JSON
def red_desde_dict(datos):
    """Valida un diccionario con la estructura JSON y devuelve el Grafo."""
    if not isinstance(datos, dict):
        raise ErrorValidacion(["La red debe ser un objeto JSON con las claves 'nodos' y 'conexiones'."])
    errores = []
    dirigido = datos.get("dirigido", False)
    if not isinstance(dirigido, bool):
        errores.append("'dirigido' debe ser true o false.")
        dirigido = False
    nodos = datos.get("nodos")
    conexiones = datos.get("conexiones", [])
    if not isinstance(nodos, list):
        errores.append("Falta la lista 'nodos'.")
        nodos = []
    if not isinstance(conexiones, list):
        errores.append("'conexiones' debe ser una lista.")
        conexiones = []
    nodos_ok = []
    for i, n in enumerate(nodos, start=1):
        if isinstance(n, dict):
            nodos_ok.append(n)
        else:
            errores.append(f"Nodo #{i}: debe ser un objeto con 'id' y 'tipo'.")
            nodos_ok.append({"id": None, "tipo": None, "_etiqueta": f"Nodo #{i}"})
    conexiones_ok = []
    for i, c in enumerate(conexiones, start=1):
        if isinstance(c, dict):
            conexiones_ok.append(c)
        else:
            errores.append(f"Conexión #{i}: debe ser un objeto con 'origen' y 'destino'.")
    grafo = _construir(dirigido, nodos_ok, conexiones_ok, errores)
    if errores:
        raise ErrorValidacion(errores)
    return grafo


def importar_json(texto):
    """Convierte un texto JSON en un Grafo validado."""
    if not isinstance(texto, str) or not texto.strip():
        raise ErrorValidacion(["El archivo JSON está vacío."])
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ErrorValidacion([f"JSON inválido: {e.msg} (línea {e.lineno}, columna {e.colno})."])
    return red_desde_dict(datos)


def exportar_json(grafo, indent=2):
    return json.dumps(grafo.a_dict(), ensure_ascii=False, indent=indent)


# ---------------------------------------------------------------- CSV
def _leer_csv(texto, columnas_obligatorias, nombre, errores):
    if not isinstance(texto, str) or not texto.strip():
        errores.append(f"El CSV de {nombre} está vacío.")
        return []
    lector = csv.DictReader(io.StringIO(texto.strip("\ufeff")))
    cabecera = [c.strip().lower() for c in (lector.fieldnames or [])]
    faltantes = [c for c in columnas_obligatorias if c not in cabecera]
    if faltantes:
        errores.append(f"El CSV de {nombre} no tiene las columnas obligatorias: {', '.join(faltantes)}.")
        return []
    filas = []
    for numero, fila in enumerate(lector, start=2):  # la fila 1 es la cabecera
        limpia = {(k or "").strip().lower(): (v or "").strip() for k, v in fila.items() if k}
        if not any(limpia.values()):
            continue  # fila en blanco
        limpia["_fila"] = numero
        filas.append(limpia)
    return filas


def _convertir_numero(texto, campo, entero=False):
    """Convierte texto de CSV a número. Lanza ErrorGrafo si no es numérico."""
    try:
        valor = float(texto)
    except ValueError:
        raise ErrorGrafo(f"'{campo}' debe ser un número (se recibió {texto!r}).")
    if entero and math.isfinite(valor) and valor == int(valor):
        return int(valor)
    return valor


def importar_csv(nodos_csv, conexiones_csv, dirigido=False):
    """Importa una red desde dos textos CSV (nodos y conexiones)."""
    errores = []
    filas_nodos = _leer_csv(nodos_csv, COLUMNAS_NODOS, "nodos", errores)
    filas_con = _leer_csv(conexiones_csv, OBLIGATORIAS_CONEXIONES, "conexiones", errores)
    nodos = [{"id": f["id"], "tipo": f["tipo"].lower(), "_etiqueta": f"Nodos, fila {f['_fila']}"}
             for f in filas_nodos]
    conexiones = []
    for f in filas_con:
        etiqueta = f"Conexiones, fila {f['_fila']}"
        conexion = {"origen": f["origen"], "destino": f["destino"], "_etiqueta": etiqueta}
        try:
            for campo in ("peso", "frecuencia", "eventos"):
                if f.get(campo, "") != "":
                    conexion[campo] = _convertir_numero(f[campo], campo, entero=(campo == "eventos"))
        except ErrorGrafo as e:
            errores.append(f"{etiqueta}: {e}")
            continue
        conexiones.append(conexion)
    grafo = _construir(dirigido, nodos, conexiones, errores)
    if errores:
        raise ErrorValidacion(errores)
    return grafo


def exportar_csv(grafo):
    """Devuelve (texto_csv_nodos, texto_csv_conexiones)."""
    salida_n = io.StringIO()
    escritor = csv.writer(salida_n, lineterminator="\n")
    escritor.writerow(COLUMNAS_NODOS)
    for n in grafo.nodos():
        escritor.writerow([n, grafo.tipo_nodo(n)])
    salida_c = io.StringIO()
    escritor = csv.writer(salida_c, lineterminator="\n")
    escritor.writerow(COLUMNAS_CONEXIONES)
    for c in grafo.conexiones():
        escritor.writerow([c["origen"], c["destino"], c["peso"], c["frecuencia"], c["eventos"]])
    return salida_n.getvalue(), salida_c.getvalue()
