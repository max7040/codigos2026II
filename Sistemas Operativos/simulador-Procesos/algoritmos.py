from collections import deque
from typing import List, Optional, Tuple

from pasos import RegistroPasos
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
# Funciones auxiliares para construir las explicaciones (paso a paso)
# ---------------------------------------------------------------------------
def _comparacion(disponibles, valor) -> str:
    """Ejemplo: 'P1=5, P2=3, P3=1'."""
    return ", ".join(f"{p.id}={valor(p)}" for p in disponibles)


def _hay_empate(disponibles, elegido, valor) -> bool:
    iguales = [p for p in disponibles if valor(p) == valor(elegido)]
    return len(iguales) > 1


def _explicar_ocio(siguiente_llegada: int) -> str:
    return (f"No hay procesos listos. La CPU queda inactiva hasta t={siguiente_llegada}, "
            "cuando llega el próximo proceso.")


def _explicar_fcfs(elegido, disponibles) -> str:
    texto = (f"Se selecciona {elegido.id} porque es el proceso disponible que llegó "
             f"primero (llegada = {elegido.llegada}). Llegadas comparadas: "
             f"{_comparacion(disponibles, lambda p: p.llegada)}.")
    if _hay_empate(disponibles, elegido, lambda p: p.llegada):
        texto += " Hubo empate de llegada: se respeta el orden en que se ingresaron."
    return texto


def _explicar_sjf(elegido, disponibles) -> str:
    texto = (f"Se selecciona {elegido.id} porque tiene el menor tiempo de ejecución "
             f"({elegido.ejecucion}) entre los procesos disponibles. Ráfagas comparadas: "
             f"{_comparacion(disponibles, lambda p: p.ejecucion)}.")
    if _hay_empate(disponibles, elegido, lambda p: p.ejecucion):
        texto += " Hubo empate de ráfaga: se desempata por menor llegada y luego por ID."
    return texto


def _explicar_prioridad(elegido, disponibles) -> str:
    texto = (f"Se selecciona {elegido.id} porque tiene la prioridad más alta entre los "
             f"procesos disponibles (prioridad {elegido.prioridad}; 1 es la más alta). "
             f"Prioridades comparadas: {_comparacion(disponibles, lambda p: p.prioridad)}.")
    if _hay_empate(disponibles, elegido, lambda p: p.prioridad):
        texto += " Hubo empate de prioridad: se desempata por menor llegada y luego por ID."
    return texto


def _explicar_expulsivo(elegido, anterior, nuevos, razon, contra):
    """
    Devuelve (evento, explicación) para SRTF y Prioridad expulsiva.
      razon(p)         -> frase de por qué p es el mejor disponible
      contra(e, otro)  -> frase de por qué e es mejor que 'otro'
    """
    if anterior is None:
        evento = "Selección (CPU libre)"
        texto = f"Se selecciona {elegido.id} porque {razon(elegido)}."
    elif anterior.restante == 0:
        evento = f"Finalización de {anterior.id}"
        texto = f"{anterior.id} terminó. Se selecciona {elegido.id} porque {razon(elegido)}."
    elif elegido is anterior:
        evento = "Llegada de procesos"
        texto = (f"{elegido.id} continúa en la CPU porque {razon(elegido)}; "
                 "ningún proceso recién llegado lo supera.")
    else:
        evento = "Preempción"
        texto = f"{elegido.id} interrumpe a {anterior.id} porque {contra(elegido, anterior)}."

    if nuevos:
        texto += " Llegada de " + ", ".join(p.id for p in nuevos) + "."
    return evento, texto


def _explicar_round_robin(actual, quantum, duracion, cola_antes) -> str:
    texto = (f"Se ejecuta {actual.id} porque es el siguiente proceso de la cola "
             f"({' → '.join(cola_antes)}) y dispone de un quantum de {quantum} unidades.")
    if actual.restante == duracion:
        if duracion < quantum:
            texto += (f" Solo le quedan {duracion} unidades (menos que el quantum), "
                      "así que termina en este turno.")
        else:
            texto += " Con este turno termina su ejecución."
    else:
        texto += (f" Al agotar el quantum le quedarán {actual.restante - duracion} "
                  "unidades y volverá al final de la cola.")
    return texto


# ---------------------------------------------------------------------------
# Esquema general de los algoritmos NO expulsivos
# ---------------------------------------------------------------------------
def _planificar_no_expulsivo(procesos: List[Proceso], clave, explicar,
                             registro: Optional[RegistroPasos] = None) -> List[Segmento]:
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
            if registro is not None:
                registro.anotar(tiempo, CPU_OCIOSA, "CPU inactiva",
                                _explicar_ocio(siguiente_llegada))
            agregar_segmento(segmentos, CPU_OCIOSA, tiempo, siguiente_llegada)
            tiempo = siguiente_llegada
            continue

        elegido = min(disponibles, key=clave)

        if registro is not None:
            registro.anotar(tiempo, elegido.id, "Selección (CPU libre)",
                            explicar(elegido, disponibles))

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
def _planificar_expulsivo(procesos: List[Proceso], clave, razon, contra,
                          registro: Optional[RegistroPasos] = None) -> List[Segmento]:
    """
    En CADA unidad de tiempo se vuelve a elegir el mejor proceso disponible
    (el de menor 'clave'). Si llegó uno mejor que el actual, lo expulsa.

    Para la simulación paso a paso solo se anota una decisión cuando hay un
    evento: cambia el proceso elegido o llegó algún proceso nuevo.
    """
    segmentos: List[Segmento] = []
    tiempo = 0
    terminados = 0
    total = len(procesos)
    anterior = None          # último proceso que usó la CPU

    while terminados < total:
        disponibles = [p for p in procesos
                       if p.llegada <= tiempo and p.restante > 0]

        # CPU inactiva hasta que llegue el próximo proceso
        if not disponibles:
            siguiente_llegada = min(p.llegada for p in procesos if p.restante > 0)
            if registro is not None:
                registro.anotar(tiempo, CPU_OCIOSA, "CPU inactiva",
                                _explicar_ocio(siguiente_llegada))
            agregar_segmento(segmentos, CPU_OCIOSA, tiempo, siguiente_llegada)
            tiempo = siguiente_llegada
            anterior = None
            continue

        elegido = min(disponibles, key=clave)

        # Evento importante: cambió el proceso elegido o llegaron procesos nuevos
        if registro is not None:
            nuevos = registro.llegadas_nuevas(tiempo)
            if elegido is not anterior or nuevos:
                evento, texto = _explicar_expulsivo(elegido, anterior, nuevos,
                                                    razon, contra)
                registro.anotar(tiempo, elegido.id, evento, texto)

        if elegido.inicio is None:
            elegido.inicio = tiempo          # primera vez que usa la CPU

        # Ejecuta una unidad de tiempo
        agregar_segmento(segmentos, elegido.id, tiempo, tiempo + 1)
        elegido.restante -= 1
        tiempo += 1
        anterior = elegido

        if elegido.restante == 0:
            elegido.finalizacion = tiempo
            terminados += 1

    return segmentos


# ---------------------------------------------------------------------------
# 1. FCFS / FIFO  (no expulsivo)
# ---------------------------------------------------------------------------
def fcfs(procesos: List[Proceso], registro: Optional[RegistroPasos] = None
         ) -> List[Segmento]:
    """Primero en llegar, primero en ser atendido.
    Si dos llegan al mismo tiempo, se respeta el orden en que se ingresaron
    (min() devuelve el primero de la lista cuando hay empate)."""
    return _planificar_no_expulsivo(procesos, clave=lambda p: p.llegada,
                                    explicar=_explicar_fcfs, registro=registro)


# ---------------------------------------------------------------------------
# 2. SJF  (no expulsivo)
# ---------------------------------------------------------------------------
def sjf(procesos: List[Proceso], registro: Optional[RegistroPasos] = None
        ) -> List[Segmento]:
    """Shortest Job First: menor ráfaga. Desempate: llegada y luego ID."""
    return _planificar_no_expulsivo(
        procesos, clave=lambda p: (p.ejecucion, p.llegada, p.id),
        explicar=_explicar_sjf, registro=registro)


# ---------------------------------------------------------------------------
# 3. Prioridad no expulsiva
# ---------------------------------------------------------------------------
def prioridad_no_expulsiva(procesos: List[Proceso],
                           registro: Optional[RegistroPasos] = None
                           ) -> List[Segmento]:
    """Menor número = mayor prioridad (1 es la más alta).
    Desempate: llegada y luego ID."""
    return _planificar_no_expulsivo(
        procesos, clave=lambda p: (p.prioridad, p.llegada, p.id),
        explicar=_explicar_prioridad, registro=registro)


# ---------------------------------------------------------------------------
# 4. SRTF  (expulsivo)
# ---------------------------------------------------------------------------
def srtf(procesos: List[Proceso], registro: Optional[RegistroPasos] = None
         ) -> List[Segmento]:
    """Shortest Remaining Time First: menor tiempo restante.
    Desempate: llegada y luego ID (así el proceso actual no se expulsa
    por otro con el mismo tiempo restante que llegó después)."""
    return _planificar_expulsivo(
        procesos,
        clave=lambda p: (p.restante, p.llegada, p.id),
        razon=lambda p: f"tiene el menor tiempo restante ({p.restante})",
        contra=lambda e, o: (f"su tiempo restante ({e.restante}) es menor "
                             f"que el de {o.id} ({o.restante})"),
        registro=registro)


# ---------------------------------------------------------------------------
# 5. Prioridad expulsiva
# ---------------------------------------------------------------------------
def prioridad_expulsiva(procesos: List[Proceso],
                        registro: Optional[RegistroPasos] = None
                        ) -> List[Segmento]:
    """Si llega un proceso con prioridad MAYOR (número menor) que el que
    se está ejecutando, lo expulsa. Con la misma prioridad no hay expulsión."""
    return _planificar_expulsivo(
        procesos,
        clave=lambda p: (p.prioridad, p.llegada, p.id),
        razon=lambda p: f"tiene la prioridad más alta (prioridad {p.prioridad})",
        contra=lambda e, o: (f"su prioridad ({e.prioridad}) es superior a la "
                             f"de {o.id} ({o.prioridad})"),
        registro=registro)


# ---------------------------------------------------------------------------
# 6. Round Robin  (expulsivo, usa cola circular)
# ---------------------------------------------------------------------------
def round_robin(procesos: List[Proceso], quantum: int,
                registro: Optional[RegistroPasos] = None) -> List[Segmento]:
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
            if registro is not None:
                registro.anotar(tiempo, CPU_OCIOSA, "CPU inactiva",
                                _explicar_ocio(siguiente_llegada))
            agregar_segmento(segmentos, CPU_OCIOSA, tiempo, siguiente_llegada)
            tiempo = siguiente_llegada
            continue

        cola_antes = [p.id for p in cola]     # para mostrarla en el paso a paso
        actual = cola.popleft()
        if actual.inicio is None:
            actual.inicio = tiempo

        # Ejecuta el menor valor entre el quantum y lo que le falta
        duracion = min(quantum, actual.restante)

        if registro is not None:
            registro.anotar(
                tiempo, actual.id, f"Turno de CPU (quantum = {quantum})",
                _explicar_round_robin(actual, quantum, duracion, cola_antes),
                cola=cola_antes)

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