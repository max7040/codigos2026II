"""
pasos.py
Estructuras de datos de la simulación paso a paso.

  - Paso: una "foto" del sistema en un instante en que el algoritmo tomó
    una decisión (qué proceso usa la CPU y por qué).
  - RegistroPasos: los algoritmos lo usan para anotar cada decisión MIENTRAS
    se ejecutan, así la explicación sale de la lógica real del algoritmo.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from proceso import Proceso


@dataclass
class Paso:
    tiempo: int                                  # instante de la decisión
    ejecutando: Optional[str]                    # ID en CPU (None = CPU inactiva)
    evento: str                                  # qué provocó la decisión
    explicacion: str                             # por qué se eligió ese proceso
    listos: List[Tuple[str, int, int, int]]      # (id, restante, prioridad, llegada)
    futuros: List[Tuple[str, int]]               # (id, llegada) aún no llegan
    terminados: List[str]                        # IDs ya finalizados
    nuevos: List[Tuple[str, int]]                # (id, llegada) llegaron desde el paso anterior
    cola: List[str]                              # cola circular (solo Round Robin)
    fin: int = 0                                 # hasta cuándo dura esta decisión
    es_final: bool = False                       # True en el paso "Fin de la simulación"


class RegistroPasos:
    def __init__(self, procesos: List[Proceso]):
        self.procesos = procesos      # los mismos objetos que modifica el algoritmo
        self.pasos: List[Paso] = []
        self._vistos = set()          # IDs que ya aparecieron como "llegadas"

    def llegadas_nuevas(self, tiempo: int) -> List[Proceso]:
        """Procesos que ya llegaron (llegada <= tiempo) y aún no se anotaron."""
        nuevos = [p for p in self.procesos
                  if p.llegada <= tiempo and p.id not in self._vistos]
        return sorted(nuevos, key=lambda p: p.llegada)

    def anotar(self, tiempo: int, ejecutando: Optional[str], evento: str,
               explicacion: str, cola: Optional[List[str]] = None) -> None:
        """Guarda una foto del estado actual. Se llama ANTES de ejecutar el tramo."""
        nuevos = self.llegadas_nuevas(tiempo)
        for p in nuevos:
            self._vistos.add(p.id)

        listos = [(p.id, p.restante, p.prioridad, p.llegada)
                  for p in self.procesos if p.llegada <= tiempo and p.restante > 0]
        futuros = sorted([(p.id, p.llegada) for p in self.procesos
                          if p.llegada > tiempo], key=lambda x: x[1])
        terminados = [p.id for p in self.procesos
                      if p.finalizacion is not None and p.finalizacion <= tiempo]

        self.pasos.append(Paso(
            tiempo=tiempo,
            ejecutando=ejecutando,
            evento=evento,
            explicacion=explicacion,
            listos=listos,
            futuros=futuros,
            terminados=terminados,
            nuevos=[(p.id, p.llegada) for p in nuevos],
            cola=list(cola) if cola else [],
        ))

    def cerrar(self, tiempo_total: int) -> None:
        """Completa el 'fin' de cada paso y agrega el paso final."""
        for i in range(len(self.pasos) - 1):
            self.pasos[i].fin = self.pasos[i + 1].tiempo
        if self.pasos:
            self.pasos[-1].fin = tiempo_total

        self.anotar(tiempo_total, None, "Fin de la simulación",
                    "Todos los procesos terminaron; ya se pueden revisar los resultados.")
        final = self.pasos[-1]
        final.fin = tiempo_total
        final.es_final = True