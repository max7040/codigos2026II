"""Recursividad: factorial y Fibonacci (Semana 5 del sílabo).

Se comparan tres enfoques para Fibonacci: recursivo simple, iterativo y
dinámico (memoización y tabulación).
"""

LIMITE_FIBONACCI_RECURSIVO = 35  # evita bloquear la aplicación (crecimiento exponencial)


def factorial_recursivo(n):
    """n! de forma recursiva. Tiempo O(n). Espacio O(n) por la pila."""
    if n < 0:
        raise ValueError("El factorial no está definido para números negativos.")
    if n <= 1:
        return 1
    return n * factorial_recursivo(n - 1)


def factorial_iterativo(n):
    """n! de forma iterativa. Tiempo O(n). Espacio O(1) (sin contar el tamaño del resultado)."""
    if n < 0:
        raise ValueError("El factorial no está definido para números negativos.")
    resultado = 1
    for k in range(2, n + 1):
        resultado *= k
    return resultado


def fibonacci_recursivo(n):
    """F(n) con recursión simple. Tiempo exponencial (aprox. O(2^n)), espacio O(n).

    Se limita n para no bloquear la aplicación.
    """
    if n < 0:
        raise ValueError("Fibonacci no está definido para números negativos.")
    if n > LIMITE_FIBONACCI_RECURSIVO:
        raise ValueError(
            f"n={n} es demasiado grande para la versión recursiva simple "
            f"(máximo {LIMITE_FIBONACCI_RECURSIVO})."
        )
    return _fib_rec(n)


def _fib_rec(n):
    if n < 2:
        return n
    return _fib_rec(n - 1) + _fib_rec(n - 2)


def fibonacci_iterativo(n):
    """F(n) iterativo. Tiempo O(n). Espacio O(1)."""
    if n < 0:
        raise ValueError("Fibonacci no está definido para números negativos.")
    anterior, actual = 0, 1
    for _ in range(n):
        anterior, actual = actual, anterior + actual
    return anterior


def fibonacci_memoizado(n, memo=None):
    """F(n) con programación dinámica descendente (memoización).

    Tiempo O(n). Espacio O(n). Usa recursión, por lo que un n muy grande puede
    agotar la pila de Python.
    """
    if n < 0:
        raise ValueError("Fibonacci no está definido para números negativos.")
    if memo is None:
        memo = {}
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fibonacci_memoizado(n - 1, memo) + fibonacci_memoizado(n - 2, memo)
    return memo[n]


def fibonacci_tabulacion(n):
    """F(n) con programación dinámica ascendente (tabla). Tiempo O(n). Espacio O(n)."""
    if n < 0:
        raise ValueError("Fibonacci no está definido para números negativos.")
    if n < 2:
        return n
    tabla = [0] * (n + 1)
    tabla[1] = 1
    for i in range(2, n + 1):
        tabla[i] = tabla[i - 1] + tabla[i - 2]
    return tabla[n]
