"""Detector de amenazas SIMULADAS basado en reglas configurables.

Es un ejercicio educativo: trabaja solo con la red cargada en el programa, no
escanea ni ataca nada, y NO usa inteligencia artificial ni aprendizaje automático.
Cada alerta indica la regla activada y los datos que la justifican; un resultado
no es prueba de una amenaza real.

Estructura (datos, reglas, cálculos y presentación separados):
  - Datos de entrada:   el Grafo (estructuras/grafo.py).
  - Reglas:             funciones regla_* que devuelven hallazgos (sin riesgo ni texto).
  - Cálculo de riesgo:  calcular_riesgo(valor, umbral).
  - Presentación:       Alerta.a_dict() y la interfaz de Streamlit (Fase 3).

Riesgo: razón = valor_observado / umbral; puntaje = min(100, round(50 * razón)).
Una regla se activa cuando valor >= umbral (puntaje >= 50). Niveles:
  Bajo [50, 60) | Medio [60, 80) | Alto [80, 100) | Crítico = 100 (valor >= 2 * umbral).
"""

from dataclasses import dataclass, field

from algoritmos.divide_conquista import merge_sort

NIVELES = ("Crítico", "Alto", "Medio", "Bajo")

REGLAS = {
    "GRADO_ALTO": {
        "nombre": "Nodo con cantidad inusual de conexiones",
        "recomendacion": "Revisar si el nodo necesita realmente tantas conexiones y aplicar "
                         "el principio de mínimo privilegio y segmentación de red.",
    },
    "FRECUENCIA_ALTA": {
        "nombre": "Frecuencia de eventos superior al umbral",
        "recomendacion": "Revisar el origen del tráfico, verificar si es legítimo y considerar "
                         "límites de tasa (rate limiting) y monitoreo adicional.",
    },
    "EVENTOS_REPETIDOS": {
        "nombre": "Conexión repetida por encima del límite",
        "recomendacion": "Revisar los registros de esa conexión, confirmar que corresponde a "
                         "un uso normal y alertar al responsable del servicio.",
    },
    "CUENTA_MULTI_SERVIDOR": {
        "nombre": "Cuenta con acceso a muchos servidores",
        "recomendacion": "Revisar los permisos de la cuenta, retirar accesos innecesarios y "
                         "exigir autenticación reforzada para cuentas con alto alcance.",
    },
}


@dataclass
class ConfigDetector:
    """Umbrales de las reglas y reglas activas."""

    umbral_grado: int = 5
    umbral_frecuencia: float = 100.0
    umbral_eventos: int = 50
    umbral_servidores: int = 3
    reglas_activas: frozenset = field(default_factory=lambda: frozenset(REGLAS))

    def validar(self):
        for nombre in ("umbral_grado", "umbral_frecuencia", "umbral_eventos", "umbral_servidores"):
            valor = getattr(self, nombre)
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor <= 0:
                raise ValueError(f"{nombre} debe ser un número mayor que 0.")
        desconocidas = set(self.reglas_activas) - set(REGLAS)
        if desconocidas:
            raise ValueError(f"Reglas desconocidas: {', '.join(sorted(desconocidas))}.")


@dataclass(frozen=True)
class Alerta:
    id_alerta: str
    regla: str
    nombre_regla: str
    tipo_objetivo: str          # "nodo" o "conexion"
    objetivo: object            # id del nodo, o tupla (origen, destino)
    descripcion_objetivo: str
    valor: float
    umbral: float
    puntaje: int
    nivel: str
    datos: dict
    explicacion: str
    recomendacion: str

    def a_dict(self):
        return {
            "id": self.id_alerta, "regla": self.regla, "nombre_regla": self.nombre_regla,
            "objetivo": self.descripcion_objetivo, "tipo_objetivo": self.tipo_objetivo,
            "valor": self.valor, "umbral": self.umbral, "puntaje": self.puntaje,
            "nivel": self.nivel, "datos": self.datos, "explicacion": self.explicacion,
            "recomendacion": self.recomendacion,
        }


# ---------------------------------------------------------------- Cálculo de riesgo
def calcular_riesgo(valor, umbral):
    """Devuelve (puntaje, nivel) según la razón valor/umbral. Ver la docstring del módulo."""
    if umbral <= 0:
        raise ValueError("El umbral debe ser mayor que 0.")
    puntaje = min(100, round(50 * valor / umbral))
    if puntaje >= 100:
        nivel = "Crítico"
    elif puntaje >= 80:
        nivel = "Alto"
    elif puntaje >= 60:
        nivel = "Medio"
    else:
        nivel = "Bajo"
    return puntaje, nivel


# ---------------------------------------------------------------- Reglas (solo hallazgos)
def regla_grado_alto(grafo, config):
    for nodo in grafo.nodos():
        grado = grafo.grado(nodo)
        if grado >= config.umbral_grado:
            datos = {"grado": grado, "vecinos": grafo.vecinos(nodo)}
            if grafo.dirigido:
                datos.update(grado_entrada=grafo.grado_entrada(nodo),
                             grado_salida=grafo.grado_salida(nodo))
            yield {"tipo_objetivo": "nodo", "objetivo": nodo, "valor": grado,
                   "umbral": config.umbral_grado, "datos": datos}


def regla_frecuencia_alta(grafo, config):
    for c in grafo.conexiones():
        if c["frecuencia"] >= config.umbral_frecuencia:
            yield {"tipo_objetivo": "conexion", "objetivo": (c["origen"], c["destino"]),
                   "valor": c["frecuencia"], "umbral": config.umbral_frecuencia,
                   "datos": {"frecuencia": c["frecuencia"], "eventos": c["eventos"],
                             "peso": c["peso"]}}


def regla_eventos_repetidos(grafo, config):
    for c in grafo.conexiones():
        if c["eventos"] >= config.umbral_eventos:
            yield {"tipo_objetivo": "conexion", "objetivo": (c["origen"], c["destino"]),
                   "valor": c["eventos"], "umbral": config.umbral_eventos,
                   "datos": {"eventos": c["eventos"], "frecuencia": c["frecuencia"],
                             "peso": c["peso"]}}


def regla_cuenta_multi_servidor(grafo, config):
    for nodo in grafo.nodos():
        if grafo.tipo_nodo(nodo) != "cuenta":
            continue
        servidores = [v for v in grafo.vecinos(nodo) if grafo.tipo_nodo(v) == "servidor"]
        if len(servidores) >= config.umbral_servidores:
            yield {"tipo_objetivo": "nodo", "objetivo": nodo, "valor": len(servidores),
                   "umbral": config.umbral_servidores,
                   "datos": {"servidores_distintos": len(servidores), "servidores": servidores}}


FUNCIONES_REGLAS = {
    "GRADO_ALTO": regla_grado_alto,
    "FRECUENCIA_ALTA": regla_frecuencia_alta,
    "EVENTOS_REPETIDOS": regla_eventos_repetidos,
    "CUENTA_MULTI_SERVIDOR": regla_cuenta_multi_servidor,
}


def _descripcion(tipo_objetivo, objetivo):
    return objetivo if tipo_objetivo == "nodo" else f"{objetivo[0]} -> {objetivo[1]}"


# ---------------------------------------------------------------- Detección
def detectar(grafo, config=None):
    """Aplica las reglas activas y devuelve la lista de Alerta, de mayor a menor riesgo."""
    config = config or ConfigDetector()
    config.validar()
    pendientes = []
    for id_regla, funcion in FUNCIONES_REGLAS.items():
        if id_regla not in config.reglas_activas:
            continue
        for h in funcion(grafo, config):
            puntaje, nivel = calcular_riesgo(h["valor"], h["umbral"])
            desc = _descripcion(h["tipo_objetivo"], h["objetivo"])
            nombre = REGLAS[id_regla]["nombre"]
            explicacion = (f"Regla '{nombre}': el valor observado es {h['valor']:g} y el umbral "
                           f"configurado es {h['umbral']:g} (razón {h['valor'] / h['umbral']:.2f}).")
            pendientes.append((id_regla, nombre, h, desc, puntaje, nivel, explicacion))
    # Orden: mayor puntaje primero; desempate por regla y objetivo. Merge Sort propio.
    claves = merge_sort([(-p[4], p[0], str(p[3]), i) for i, p in enumerate(pendientes)])
    alertas = []
    for numero, (_, _, _, i) in enumerate(claves, start=1):
        id_regla, nombre, h, desc, puntaje, nivel, explicacion = pendientes[i]
        alertas.append(Alerta(
            id_alerta=f"A{numero:03d}", regla=id_regla, nombre_regla=nombre,
            tipo_objetivo=h["tipo_objetivo"], objetivo=h["objetivo"],
            descripcion_objetivo=desc, valor=h["valor"], umbral=h["umbral"],
            puntaje=puntaje, nivel=nivel, datos=h["datos"], explicacion=explicacion,
            recomendacion=REGLAS[id_regla]["recomendacion"]))
    return alertas


def nodos_con_alerta(alertas):
    """Conjunto de nodos que son objetivo directo de alguna alerta."""
    return {a.objetivo for a in alertas if a.tipo_objetivo == "nodo"}


def conexiones_con_alerta(alertas):
    """Conjunto de conexiones (origen, destino) que son objetivo de alguna alerta."""
    return {a.objetivo for a in alertas if a.tipo_objetivo == "conexion"}


def resumen_por_nivel(alertas):
    """Cuenta de alertas por nivel de riesgo (incluye niveles con cero)."""
    cuenta = {nivel: 0 for nivel in NIVELES}
    for a in alertas:
        cuenta[a.nivel] += 1
    return cuenta
