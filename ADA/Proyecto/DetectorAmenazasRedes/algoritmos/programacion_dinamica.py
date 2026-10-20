"""Programación dinámica (Semana 8 del sílabo): mochila 0/1 y cadena de matrices."""


def mochila_01(elementos, capacidad):
    """Mochila 0/1 por programación dinámica.

    elementos: lista de tuplas (nombre, valor, peso) con peso entero >= 0.
    capacidad: entero >= 0.
    tabla[i][w] = mejor valor usando los primeros i elementos con capacidad w.
    Tiempo: O(n*W). Espacio: O(n*W) (se conserva la tabla para reconstruir la solución).
    Devuelve (valor_maximo, [nombres_elegidos]).
    """
    if capacidad < 0 or int(capacidad) != capacidad:
        raise ValueError("La capacidad debe ser un entero no negativo.")
    for nombre, valor, peso in elementos:
        if peso < 0 or int(peso) != peso or valor < 0:
            raise ValueError(f"Elemento inválido: {nombre!r} (peso entero >= 0, valor >= 0).")
    n = len(elementos)
    W = int(capacidad)
    tabla = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        _, valor, peso = elementos[i - 1]
        peso = int(peso)
        for w in range(W + 1):
            tabla[i][w] = tabla[i - 1][w]
            if peso <= w and tabla[i - 1][w - peso] + valor > tabla[i][w]:
                tabla[i][w] = tabla[i - 1][w - peso] + valor
    # Reconstrucción de la solución
    elegidos = []
    w = W
    for i in range(n, 0, -1):
        if tabla[i][w] != tabla[i - 1][w]:
            nombre, _, peso = elementos[i - 1]
            elegidos.append(nombre)
            w -= int(peso)
    elegidos.reverse()
    return tabla[n][W], elegidos


def cadena_matrices(dimensiones):
    """Multiplicación de cadena de matrices (mínimo de multiplicaciones escalares).

    dimensiones: lista p de longitud n+1; la matriz A_i tiene tamaño p[i-1] x p[i].
    Tiempo: O(n^3). Espacio: O(n^2).
    Devuelve (costo_minimo, parentizacion), por ejemplo (30, '((A1A2)A3)').
    Con una sola matriz el costo es 0.
    """
    if len(dimensiones) < 2:
        raise ValueError("Se necesita al menos una matriz (2 dimensiones).")
    if any(d <= 0 or int(d) != d for d in dimensiones):
        raise ValueError("Las dimensiones deben ser enteros positivos.")
    n = len(dimensiones) - 1
    costo = [[0] * (n + 1) for _ in range(n + 1)]
    corte = [[0] * (n + 1) for _ in range(n + 1)]
    for longitud in range(2, n + 1):
        for i in range(1, n - longitud + 2):
            j = i + longitud - 1
            costo[i][j] = float("inf")
            for k in range(i, j):
                c = (costo[i][k] + costo[k + 1][j]
                     + dimensiones[i - 1] * dimensiones[k] * dimensiones[j])
                if c < costo[i][j]:
                    costo[i][j] = c
                    corte[i][j] = k

    def construir(i, j):
        if i == j:
            return f"A{i}"
        return "(" + construir(i, corte[i][j]) + construir(corte[i][j] + 1, j) + ")"

    return costo[1][n], construir(1, n)
