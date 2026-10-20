"""Algoritmos voraces (Semana 7 del sílabo): mochila fraccionaria y selección de actividades."""

from algoritmos.divide_conquista import merge_sort


def mochila_fraccionaria(elementos, capacidad):
    """Problema de la mochila fraccionaria.

    elementos: lista de tuplas (nombre, valor, peso) con peso > 0.
    Criterio voraz: tomar primero lo de mayor valor/peso, fraccionando el último.
    Es óptimo para la versión fraccionaria.
    Tiempo: O(n log n) por el ordenamiento. Espacio: O(n).
    Devuelve (valor_total, [(nombre, fraccion_tomada), ...]).
    """
    if capacidad < 0:
        raise ValueError("La capacidad no puede ser negativa.")
    for nombre, valor, peso in elementos:
        if peso <= 0 or valor < 0:
            raise ValueError(f"Elemento inválido: {nombre!r} (peso>0 y valor>=0).")
    # Se ordena por razón valor/peso descendente usando el Merge Sort propio.
    claves = merge_sort([(-valor / peso, i) for i, (_, valor, peso) in enumerate(elementos)])
    restante = capacidad
    total = 0.0
    tomados = []
    for _, i in claves:
        if restante <= 0:
            break
        nombre, valor, peso = elementos[i]
        fraccion = min(1.0, restante / peso)
        total += valor * fraccion
        restante -= peso * fraccion
        tomados.append((nombre, fraccion))
    return total, tomados


def seleccion_actividades(actividades):
    """Selección de actividades (máximo número de actividades compatibles).

    actividades: lista de tuplas (nombre, inicio, fin) con inicio <= fin.
    Criterio voraz: ordenar por hora de fin y elegir la siguiente compatible.
    Es óptimo. Tiempo: O(n log n). Espacio: O(n).
    Dos actividades son compatibles si inicio_siguiente >= fin_anterior.
    """
    for nombre, inicio, fin in actividades:
        if inicio > fin:
            raise ValueError(f"Actividad inválida: {nombre!r} (inicio > fin).")
    ordenadas = merge_sort([(fin, inicio, nombre) for nombre, inicio, fin in actividades])
    seleccion = []
    ultimo_fin = None
    for fin, inicio, nombre in ordenadas:
        if ultimo_fin is None or inicio >= ultimo_fin:
            seleccion.append((nombre, inicio, fin))
            ultimo_fin = fin
    return seleccion
