"""Algoritmos de ordenamiento elementales (Semana 3 del sílabo).

Todas las funciones reciben una lista y devuelven una NUEVA lista ordenada
de menor a mayor; la lista original no se modifica. Se implementan a mano,
sin usar sorted() ni list.sort().
"""


def burbuja(datos):
    """Ordenamiento burbuja con corte anticipado.

    Objetivo: comparar pares adyacentes e intercambiarlos si están desordenados.
    Tiempo: mejor caso O(n) (ya ordenada), promedio y peor caso O(n^2).
    Espacio: O(1) adicional (además de la copia de salida).
    """
    a = list(datos)
    n = len(a)
    for i in range(n - 1):
        hubo_cambio = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                hubo_cambio = True
        if not hubo_cambio:
            break
    return a


def insercion(datos):
    """Ordenamiento por inserción.

    Objetivo: construir una parte izquierda ordenada insertando cada elemento
    en su posición correcta.
    Tiempo: mejor caso O(n), promedio y peor caso O(n^2).
    Espacio: O(1) adicional.
    """
    a = list(datos)
    for i in range(1, len(a)):
        clave = a[i]
        j = i - 1
        while j >= 0 and a[j] > clave:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = clave
    return a


def seleccion(datos):
    """Ordenamiento por selección.

    Objetivo: en cada paso seleccionar el mínimo del resto y colocarlo al frente.
    Tiempo: O(n^2) en mejor, promedio y peor caso.
    Espacio: O(1) adicional.
    """
    a = list(datos)
    n = len(a)
    for i in range(n - 1):
        indice_min = i
        for j in range(i + 1, n):
            if a[j] < a[indice_min]:
                indice_min = j
        if indice_min != i:
            a[i], a[indice_min] = a[indice_min], a[i]
    return a
