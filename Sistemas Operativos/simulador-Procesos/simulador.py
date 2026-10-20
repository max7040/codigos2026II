"""
simulador.py
Intermediario entre la interfaz y los algoritmos.

Recibe los procesos, el algoritmo elegido y el quantum, y devuelve un
ResultadoSimulacion con todo lo que la interfaz necesita mostrar.
También ofrece la simulación paso a paso (simular_paso_a_paso).
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from algoritmos import (Segmento, fcfs, prioridad_expulsiva,
                        prioridad_no_expulsiva, round_robin, sjf, srtf)
from pasos import Paso, RegistroPasos
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
    tiempo_cpu_ocupada: int            # unidades con la CPU trabajando
    tiempo_cpu_inactiva: int           # unidades con la CPU sin proceso
    procesos_completados: int          # cantidad de procesos que terminaron


@dataclass
class SimulacionPasos:
    algoritmo: str
    quantum: Optional[int]
    resultado: ResultadoSimulacion     # resultado completo (se muestra en el último paso)
    pasos: List[Paso]                  # decisiones registradas por el algoritmo


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
# Validaciones y ejecución compartida
# ---------------------------------------------------------------------------
def validar_procesos(procesos: List[Proceso]) -> None:
    """Revisa los datos de los procesos. Lanza ValueError si algo es inválido."""
    if not procesos:
        raise ValueError("No hay procesos para simular.")
    ids_usados = set()
    for p in procesos:
        if not str(p.id).strip():
            raise ValueError("Hay un proceso con ID vacío.")
        if p.id.lower() in ids_usados:
            raise ValueError(f"El ID '{p.id}' está repetido.")
        ids_usados.add(p.id.lower())
        if p.llegada < 0:
            raise ValueError(f"{p.id}: el tiempo de llegada no puede ser negativo.")
        if p.ejecucion <= 0:
            raise ValueError(f"{p.id}: el tiempo de ejecución debe ser mayor que 0.")
        if p.prioridad <= 0:
            raise ValueError(f"{p.id}: la prioridad debe ser mayor que 0.")


def _ejecutar_algoritmo(copias: List[Proceso], nombre_algoritmo: str,
                        quantum: Optional[int],
                        registro: Optional[RegistroPasos] = None) -> List[Segmento]:
    """Llama al algoritmo elegido. Si hay 'registro', anota las decisiones."""
    if nombre_algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo desconocido: {nombre_algoritmo}")
    funcion = ALGORITMOS[nombre_algoritmo]

    if nombre_algoritmo == ROUND_ROBIN:
        if quantum is None or quantum <= 0:
            raise ValueError("El quantum debe ser mayor que 0.")
        return funcion(copias, quantum, registro)
    return funcion(copias, registro)


def _construir_resultado(copias: List[Proceso],
                         segmentos: List[Segmento]) -> ResultadoSimulacion:
    for proceso in copias:
        proceso.calcular_metricas()

    tiempo_total = calcular_tiempo_total(segmentos)
    cpu_ocupada = sum(fin - inicio for id_proceso, inicio, fin in segmentos
                      if id_proceso is not None)

    return ResultadoSimulacion(
        procesos=copias,
        segmentos=segmentos,
        orden=obtener_orden_ejecucion(segmentos),
        promedio_espera=_promedio([p.espera for p in copias]),
        promedio_retorno=_promedio([p.retorno for p in copias]),
        promedio_respuesta=_promedio([p.respuesta for p in copias]),
        tiempo_total=tiempo_total,
        utilizacion_cpu=calcular_utilizacion(segmentos),
        tiempo_cpu_ocupada=cpu_ocupada,
        tiempo_cpu_inactiva=tiempo_total - cpu_ocupada,
        procesos_completados=sum(1 for p in copias if p.finalizacion is not None),
    )


# ---------------------------------------------------------------------------
# Funciones principales
# ---------------------------------------------------------------------------
def simular(procesos: List[Proceso], nombre_algoritmo: str,
            quantum: Optional[int] = None) -> ResultadoSimulacion:
    """Ejecuta un algoritmo sobre una COPIA de los procesos."""
    validar_procesos(procesos)
    copias = [p.copia() for p in procesos]
    segmentos = _ejecutar_algoritmo(copias, nombre_algoritmo, quantum)
    return _construir_resultado(copias, segmentos)


def simular_paso_a_paso(procesos: List[Proceso], nombre_algoritmo: str,
                        quantum: Optional[int] = None) -> SimulacionPasos:
    """
    Ejecuta el MISMO algoritmo que simular(), pero con un registro que anota
    cada decisión. La interfaz navega después por esos pasos.
    """
    validar_procesos(procesos)
    copias = [p.copia() for p in procesos]
    registro = RegistroPasos(copias)
    segmentos = _ejecutar_algoritmo(copias, nombre_algoritmo, quantum, registro)
    resultado = _construir_resultado(copias, segmentos)
    registro.cerrar(resultado.tiempo_total)
    return SimulacionPasos(nombre_algoritmo, quantum, resultado, registro.pasos)


def segmentos_hasta(segmentos: List[Segmento], tiempo_limite: int) -> List[Segmento]:
    """Parte de los segmentos reales que ocurre antes de 'tiempo_limite'."""
    recortados = []
    for id_proceso, inicio, fin in segmentos:
        if inicio >= tiempo_limite:
            break
        recortados.append((id_proceso, inicio, min(fin, tiempo_limite)))
    return recortados


def segmentos_del_paso(simulacion: SimulacionPasos, indice: int) -> List[Segmento]:
    """Gantt acumulado hasta el final del paso 'indice'."""
    paso = simulacion.pasos[indice]
    return segmentos_hasta(simulacion.resultado.segmentos, paso.fin)


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