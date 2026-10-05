from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Proceso:
    # ----- Datos originales (los ingresa el usuario) -----
    id: str
    llegada: int
    ejecucion: int
    prioridad: int

    # ----- Resultados (se llenan durante/después de la simulación) -----
    inicio: Optional[int] = None        # Primer instante en que usa la CPU
    finalizacion: Optional[int] = None  # Instante en que termina
    retorno: Optional[int] = None
    espera: Optional[int] = None
    respuesta: Optional[int] = None

    # Tiempo que le falta ejecutar (lo usan los algoritmos expulsivos)
    restante: int = field(init=False, default=0)

    def __post_init__(self):
        self.restante = self.ejecucion

    def calcular_metricas(self):
        """Calcula retorno, espera y respuesta con las fórmulas del curso."""
        self.retorno = self.finalizacion - self.llegada
        self.espera = self.retorno - self.ejecucion
        self.respuesta = self.inicio - self.llegada

    def copia(self):
        """Devuelve una copia limpia (sin resultados) del proceso."""
        return Proceso(self.id, self.llegada, self.ejecucion, self.prioridad)