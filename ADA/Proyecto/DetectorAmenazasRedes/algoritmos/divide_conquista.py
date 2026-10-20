"""Divide y vencerás: Merge Sort y Quick Sort (Semana 6 del sílabo).

Ambas funciones devuelven una NUEVA lista ordenada sin modificar la original.
"""


def _mezclar(izq, der):
    """Mezcla dos listas ordenadas en una sola lista ordenada. Tiempo O(n)."""
    resultado = []
    i = j = 0
    while i < len(izq) and j < len(der):
        if izq[i] <= der[j]:  # '<=' mantiene la estabilidad
            resultado.append(izq[i])
            i += 1
        else:
            resultado.append(der[j])
            j += 1
    resultado.extend(izq[i:])
    resultado.extend(der[j:])
    return resultado


def merge_sort(datos):
    """Merge Sort.

    Estrategia: dividir la lista a la mitad, ordenar cada mitad recursivamente
    y combinar con _mezclar.
    Recurrencia: T(n) = 2T(n/2) + O(n).
    Tiempo: O(n log n) en mejor, promedio y peor caso.
    Espacio: O(n) adicional. Es estable.
    """
    if len(datos) <= 1:
        return list(datos)
    medio = len(datos) // 2
    return _mezclar(merge_sort(datos[:medio]), merge_sort(datos[medio:]))


def quick_sort(datos):
    """Quick Sort in situ (sobre una copia) con pivote de mediana de tres.

    Estrategia: elegir un pivote, particionar (menores a la izquierda, mayores
    a la derecha) y ordenar recursivamente las partes. Se recurre sobre la parte
    más pequeña y se itera sobre la mayor para limitar la profundidad de pila.
    Tiempo: promedio O(n log n); peor caso O(n^2) (particiones muy desbalanceadas).
    Espacio: O(log n) de pila. No es estable.
    """
    a = list(datos)
    _quick(a, 0, len(a) - 1)
    return a


def _mediana_de_tres(a, bajo, alto):
    medio = (bajo + alto) // 2
    if a[medio] < a[bajo]:
        a[medio], a[bajo] = a[bajo], a[medio]
    if a[alto] < a[bajo]:
        a[alto], a[bajo] = a[bajo], a[alto]
    if a[alto] < a[medio]:
        a[alto], a[medio] = a[medio], a[alto]
    return medio  # a[medio] es la mediana de los tres


def _particionar(a, bajo, alto):
    """Partición de Lomuto. Devuelve la posición final del pivote."""
    medio = _mediana_de_tres(a, bajo, alto)
    a[medio], a[alto] = a[alto], a[medio]  # pivote al final
    pivote = a[alto]
    i = bajo
    for j in range(bajo, alto):
        if a[j] < pivote:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[alto] = a[alto], a[i]
    return i


def _quick(a, bajo, alto):
    while bajo < alto:
        p = _particionar(a, bajo, alto)
        if p - bajo < alto - p:
            _quick(a, bajo, p - 1)
            bajo = p + 1
        else:
            _quick(a, p + 1, alto)
            alto = p - 1
