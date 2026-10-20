"""Experimentos reproducibles de ordenamiento (EV1 y Módulo H).

- Cada algoritmo recibe una COPIA de los mismos datos.
- Los datos se generan con una semilla fija (reproducibles).
- El tiempo se mide con time.perf_counter().
- Cada resultado se verifica contra sorted() (solo como comprobación; los
  algoritmos evaluados son implementaciones propias).
- Los tiempos dependen del equipo y del intérprete: no son la complejidad teórica.
"""

import random
import time

from algoritmos.divide_conquista import merge_sort, quick_sort
from algoritmos.ordenamiento import burbuja, insercion, seleccion

ALGORITMOS = {
    "Burbuja": burbuja,
    "Inserción": insercion,
    "Selección": seleccion,
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
}

TIPOS_DATOS = ("aleatorio", "ordenado", "inverso", "con_repetidos")


def generar_datos(n, tipo="aleatorio", semilla=42):
    """Genera una lista de n enteros del tipo indicado, de forma reproducible."""
    if n < 0:
        raise ValueError("El tamaño no puede ser negativo.")
    rng = random.Random(semilla)
    if tipo == "aleatorio":
        return [rng.randint(0, max(n * 10, 1)) for _ in range(n)]
    if tipo == "ordenado":
        return list(range(n))
    if tipo == "inverso":
        return list(range(n, 0, -1))
    if tipo == "con_repetidos":
        return [rng.randint(0, max(n // 10, 1)) for _ in range(n)]
    raise ValueError(f"Tipo de datos desconocido: {tipo!r}. Opciones: {TIPOS_DATOS}.")


def medir(algoritmo, datos, repeticiones=3):
    """Ejecuta el algoritmo sobre copias de 'datos' y devuelve (tiempos, correcto).

    tiempos: lista con el tiempo (segundos) de cada repetición.
    correcto: True si el resultado coincide con sorted(datos) en todas las repeticiones.
    """
    if repeticiones < 1:
        raise ValueError("Debe haber al menos una repetición.")
    esperado = sorted(datos)
    tiempos, correcto = [], True
    for _ in range(repeticiones):
        copia = list(datos)
        inicio = time.perf_counter()
        resultado = algoritmo(copia)
        tiempos.append(time.perf_counter() - inicio)
        if resultado != esperado:
            correcto = False
    return tiempos, correcto


def ejecutar_benchmark(nombres=None, tamanos=(100, 500, 1000), tipos=("aleatorio",),
                       repeticiones=3, semilla=42):
    """Ejecuta el experimento completo.

    Devuelve una lista de registros (dict) con: algoritmo, tipo, n, repeticiones,
    mejor, promedio y peor tiempo (segundos) y si el resultado fue correcto.
    """
    nombres = list(nombres) if nombres is not None else list(ALGORITMOS)
    for nombre in nombres:
        if nombre not in ALGORITMOS:
            raise ValueError(f"Algoritmo desconocido: {nombre!r}.")
    registros = []
    for tipo in tipos:
        for n in tamanos:
            datos = generar_datos(n, tipo, semilla)  # mismos datos para todos
            for nombre in nombres:
                tiempos, correcto = medir(ALGORITMOS[nombre], datos, repeticiones)
                registros.append({
                    "algoritmo": nombre,
                    "tipo": tipo,
                    "n": n,
                    "repeticiones": repeticiones,
                    "mejor_s": min(tiempos),
                    "promedio_s": sum(tiempos) / len(tiempos),
                    "peor_s": max(tiempos),
                    "correcto": correcto,
                })
    return registros
