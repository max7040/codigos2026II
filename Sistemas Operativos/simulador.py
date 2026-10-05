"""
simulador.py
Intermediario entre la interfaz y los algoritmos.

Recibe los procesos, el algoritmo elegido y el quantum, y devuelve un
ResultadoSimulacion con todo lo que la interfaz necesita mostrar.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from algoritmos import (Segmento, fcfs, prioridad_expulsiva,
                        prioridad_no_expulsiva, round_robin, sjf, srtf)
from proceso import Proceso

ROUND_ROBIN = "Round Robin"

# Nombre que se muestra en la interfaz -> función que lo implementa
ALGORITMOS = {
    "FCFS": fcfs,
    "SJF": sjf,
    "Prioridad no expulsiva": prioridad_no_expulsiva,
    "SRTF": srtf,
    "Prioridad expulsiva": prioridad_expulsiva,
    ROUND_ROBIN: round_robin,
}

# Tipo de cada algoritmo (se muestra en la interfaz)
TIPOS = {
    "FCFS": "No expulsivo",
    "SJF": "No expulsivo",
    "Prioridad no expulsiva": "No expulsivo",
    "SRTF": "Expulsivo",
    "Prioridad expulsiva": "Expulsivo",
    ROUND_ROBIN: "Expulsivo",
}


@dataclass
class ResultadoSimulacion:
    procesos: List[Proceso]            # procesos con inicio, fin, retorno, etc.
    segmentos: List[Segmento]          # segmentos del Gantt: (id, inicio, fin)
    orden: List[Optional[str]]         # orden de ejecución (None = CPU inactiva)
    promedio_espera: float
    promedio_retorno: float
    promedio_respuesta: float
    tiempo_total: int
    utilizacion_cpu: float             # porcentaje (0 a 100)


# ---------------------------------------------------------------------------
# Cálculos sobre los resultados
# ---------------------------------------------------------------------------
def _promedio(valores: List[int]) -> float:
    return sum(valores) / len(valores)


def calcular_tiempo_total(segmentos: List[Segmento]) -> int:
    """El tiempo total es el instante en que termina el último segmento."""
    if not segmentos:
        return 0
    return segmentos[-1][2]


def calcular_utilizacion(segmentos: List[Segmento]) -> float:
    """Utilización = tiempo con CPU ocupada / tiempo total * 100."""
    total = calcular_tiempo_total(segmentos)
    if total == 0:
        return 0.0
    ocupado = sum(fin - inicio for id_proceso, inicio, fin in segmentos
                  if id_proceso is not None)
    return ocupado / total * 100


def obtener_orden_ejecucion(segmentos: List[Segmento]) -> List[Optional[str]]:
    return [id_proceso for id_proceso, _, _ in segmentos]


# ---------------------------------------------------------------------------
# Funciones principales
# ---------------------------------------------------------------------------
def simular(procesos: List[Proceso], nombre_algoritmo: str,
            quantum: Optional[int] = None) -> ResultadoSimulacion:
    """Ejecuta un algoritmo sobre una COPIA de los procesos."""
    if not procesos:
        raise ValueError("No hay procesos para simular.")
    if nombre_algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo desconocido: {nombre_algoritmo}")

    copias = [p.copia() for p in procesos]
    funcion = ALGORITMOS[nombre_algoritmo]

    if nombre_algoritmo == ROUND_ROBIN:
        if quantum is None or quantum <= 0:
            raise ValueError("El quantum debe ser mayor que 0.")
        segmentos = funcion(copias, quantum)
    else:
        segmentos = funcion(copias)

    for proceso in copias:
        proceso.calcular_metricas()

    return ResultadoSimulacion(
        procesos=copias,
        segmentos=segmentos,
        orden=obtener_orden_ejecucion(segmentos),
        promedio_espera=_promedio([p.espera for p in copias]),
        promedio_retorno=_promedio([p.retorno for p in copias]),
        promedio_respuesta=_promedio([p.respuesta for p in copias]),
        tiempo_total=calcular_tiempo_total(segmentos),
        utilizacion_cpu=calcular_utilizacion(segmentos),
    )


def comparar_algoritmos(procesos: List[Proceso], quantum: int
                        ) -> List[Tuple[str, float, float, float]]:
    """
    Ejecuta los mismos procesos con los seis algoritmos.
    Devuelve una fila por algoritmo:
    (nombre, espera promedio, retorno promedio, respuesta promedio)
    """
    filas = []
    for nombre in ALGORITMOS:
        resultado = simular(procesos, nombre, quantum)
        filas.append((nombre,
                      resultado.promedio_espera,
                      resultado.promedio_retorno,
                      resultado.promedio_respuesta))
    return filas