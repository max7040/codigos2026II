from collections import deque
from typing import List, Optional, Tuple

from proceso import Proceso

Segmento = Tuple[Optional[str], int, int]
CPU_OCIOSA = None


# ---------------------------------------------------------------------------
# Función auxiliar compartida
# ---------------------------------------------------------------------------
def agregar_segmento(segmentos: List[Segmento], id_proceso: Optional[str],
                     inicio: int, fin: int) -> None:
    """
    Agrega un segmento a la lista. Si el segmento anterior es del mismo
    proceso y termina justo donde este empieza, los une en uno solo.
    """
    if fin <= inicio:
        return
    if segmentos:
        ultimo_id, ultimo_inicio, ultimo_fin = segmentos[-1]
        if ultimo_id == id_proceso and ultimo_fin == inicio:
            segmentos[-1] = (ultimo_id, ultimo_inicio, fin)
            return
    segmentos.append((id_proceso, inicio, fin))


# ---------------------------------------------------------------------------
# Esquema general de los algoritmos NO expulsivos
# ---------------------------------------------------------------------------
def _planificar_no_expulsivo(procesos: List[Proceso], clave) -> List[Segmento]:
    """
    Cada vez que la CPU queda libre se elige, entre los procesos que ya
    llegaron, el que tenga la menor 'clave'. Ese proceso se ejecuta completo.
    """
    pendientes = list(procesos)
    segmentos: List[Segmento] = []
    tiempo = 0

    while pendientes:
        disponibles = [p for p in pendientes if p.llegada <= tiempo]

        # Nadie ha llegado todavía: la CPU queda inactiva hasta la próxima llegada
        if not disponibles:
            siguiente_llegada = min(p.llegada for p in pendientes)
            agregar_segmento(segmentos, CPU_OCIOSA, tiempo, siguiente_llegada)
            tiempo = siguiente_llegada
            continue

        elegido = min(disponibles, key=clave)
        elegido.inicio = tiempo
        tiempo += elegido.ejecucion
        elegido.finalizacion = tiempo
        elegido.restante = 0
        agregar_segmento(segmentos, elegido.id, elegido.inicio, tiempo)
        pendientes.remove(elegido)

    return segmentos


# ---------------------------------------------------------------------------
# Esquema general de los algoritmos EXPULSIVOS (SRTF y Prioridad expulsiva)
# ---------------------------------------------------------------------------
def _planificar_expulsivo(procesos: List[Proceso], clave) -> List[Segmento]:
    """
    En CADA unidad de tiempo se vuelve a elegir el mejor proceso disponible
    (el de menor 'clave'). Si llegó uno mejor que el actual, lo expulsa.
    """
    segmentos: List[Segmento] = []
    tiempo = 0
    terminados = 0
    total = len(procesos)

    while terminados < total:
        disponibles = [p for p in procesos
                       if p.llegada <= tiempo and p.restante > 0]

        # CPU inactiva hasta que llegue el próximo proceso
        if not disponibles:
            siguiente_llegada = min(p.llegada for p in procesos if p.restante > 0)
            agregar_segmento(segmentos, CPU_OCIOSA, tiempo, siguiente_llegada)
            tiempo = siguiente_llegada
            continue

        elegido = min(disponibles, key=clave)
        if elegido.inicio is None:
            elegido.inicio = tiempo          # primera vez que usa la CPU

        # Ejecuta una unidad de tiempo
        agregar_segmento(segmentos, elegido.id, tiempo, tiempo + 1)
        elegido.restante -= 1
        tiempo += 1

        if elegido.restante == 0:
            elegido.finalizacion = tiempo
            terminados += 1

    return segmentos


# ---------------------------------------------------------------------------
# 1. FCFS / FIFO  (no expulsivo)
# ---------------------------------------------------------------------------
def fcfs(procesos: List[Proceso]) -> List[Segmento]:
    """Primero en llegar, primero en ser atendido.
    Si dos llegan al mismo tiempo, se respeta el orden en que se ingresaron
    (min() devuelve el primero de la lista cuando hay empate)."""
    return _planificar_no_expulsivo(procesos, clave=lambda p: p.llegada)


# ---------------------------------------------------------------------------
# 2. SJF  (no expulsivo)
# ---------------------------------------------------------------------------
def sjf(procesos: List[Proceso]) -> List[Segmento]:
    """Shortest Job First: menor ráfaga. Desempate: llegada y luego ID."""
    return _planificar_no_expulsivo(
        procesos, clave=lambda p: (p.ejecucion, p.llegada, p.id))


# ---------------------------------------------------------------------------
# 3. Prioridad no expulsiva
# ---------------------------------------------------------------------------
def prioridad_no_expulsiva(procesos: List[Proceso]) -> List[Segmento]:
    """Menor número = mayor prioridad (1 es la más alta).
    Desempate: llegada y luego ID."""
    return _planificar_no_expulsivo(
        procesos, clave=lambda p: (p.prioridad, p.llegada, p.id))


# ---------------------------------------------------------------------------
# 4. SRTF  (expulsivo)
# ---------------------------------------------------------------------------
def srtf(procesos: List[Proceso]) -> List[Segmento]:
    """Shortest Remaining Time First: menor tiempo restante.
    Desempate: llegada y luego ID (así el proceso actual no se expulsa
    por otro con el mismo tiempo restante que llegó después)."""
    return _planificar_expulsivo(
        procesos, clave=lambda p: (p.restante, p.llegada, p.id))


# ---------------------------------------------------------------------------
# 5. Prioridad expulsiva
# ---------------------------------------------------------------------------
def prioridad_expulsiva(procesos: List[Proceso]) -> List[Segmento]:
    """Si llega un proceso con prioridad MAYOR (número menor) que el que
    se está ejecutando, lo expulsa. Con la misma prioridad no hay expulsión."""
    return _planificar_expulsivo(
        procesos, clave=lambda p: (p.prioridad, p.llegada, p.id))


# ---------------------------------------------------------------------------
# 6. Round Robin  (expulsivo, usa cola circular)
# ---------------------------------------------------------------------------
def round_robin(procesos: List[Proceso], quantum: int) -> List[Segmento]:
    """
    Cada proceso usa la CPU como máximo 'quantum' unidades y, si no termina,
    vuelve al final de la cola.
    Regla de desempate: los procesos que llegan mientras otro se ejecuta
    entran a la cola ANTES de que el proceso expulsado vuelva a ella.
    """
    por_llegar = sorted(procesos, key=lambda p: p.llegada)  # orden estable
    cola = deque()
    segmentos: List[Segmento] = []
    tiempo = 0
    terminados = 0
    indice = 0                      # siguiente proceso que aún no entró a la cola
    total = len(procesos)

    while terminados < total:
        # Pasar a la cola todos los procesos que ya llegaron
        while indice < total and por_llegar[indice].llegada <= tiempo:
            cola.append(por_llegar[indice])
            indice += 1

        # Cola vacía: CPU inactiva hasta la próxima llegada
        if not cola:
            siguiente_llegada = por_llegar[indice].llegada
            agregar_segmento(segmentos, CPU_OCIOSA, tiempo, siguiente_llegada)
            tiempo = siguiente_llegada
            continue

        actual = cola.popleft()
        if actual.inicio is None:
            actual.inicio = tiempo

        # Ejecuta el menor valor entre el quantum y lo que le falta
        duracion = min(quantum, actual.restante)
        agregar_segmento(segmentos, actual.id, tiempo, tiempo + duracion)
        tiempo += duracion
        actual.restante -= duracion

        # Los que llegaron durante esta ejecución entran primero a la cola
        while indice < total and por_llegar[indice].llegada <= tiempo:
            cola.append(por_llegar[indice])
            indice += 1

        if actual.restante > 0:
            cola.append(actual)             # vuelve al final de la cola
        else:
            actual.finalizacion = tiempo
            terminados += 1

    return segmentos