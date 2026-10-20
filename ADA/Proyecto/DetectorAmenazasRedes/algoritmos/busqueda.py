"""Búsqueda lineal y binaria (Semana 4 del sílabo).

Todas devuelven el índice del elemento o -1 si no está presente.
"""


def busqueda_lineal(datos, objetivo):
    """Recorre la lista de izquierda a derecha.

    Tiempo: mejor caso O(1), promedio y peor caso O(n). Espacio: O(1).
    No requiere que la lista esté ordenada.
    """
    for i, valor in enumerate(datos):
        if valor == objetivo:
            return i
    return -1


def busqueda_binaria(datos_ordenados, objetivo):
    """Búsqueda binaria iterativa. REQUIERE lista ordenada ascendentemente.

    Descarta la mitad del intervalo en cada paso.
    Tiempo: mejor caso O(1), promedio y peor caso O(log n). Espacio: O(1).
    Con elementos repetidos devuelve el índice de alguna de las coincidencias.
    """
    bajo, alto = 0, len(datos_ordenados) - 1
    while bajo <= alto:
        medio = (bajo + alto) // 2
        if datos_ordenados[medio] == objetivo:
            return medio
        if datos_ordenados[medio] < objetivo:
            bajo = medio + 1
        else:
            alto = medio - 1
    return -1


def busqueda_binaria_recursiva(datos_ordenados, objetivo, bajo=0, alto=None):
    """Versión recursiva de la búsqueda binaria.

    Tiempo: O(log n). Espacio: O(log n) por la pila de llamadas.
    """
    if alto is None:
        alto = len(datos_ordenados) - 1
    if bajo > alto:
        return -1
    medio = (bajo + alto) // 2
    if datos_ordenados[medio] == objetivo:
        return medio
    if datos_ordenados[medio] < objetivo:
        return busqueda_binaria_recursiva(datos_ordenados, objetivo, medio + 1, alto)
    return busqueda_binaria_recursiva(datos_ordenados, objetivo, bajo, medio - 1)
