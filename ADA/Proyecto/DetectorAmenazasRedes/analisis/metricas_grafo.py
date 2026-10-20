"""Métricas y comparación de representaciones de grafos (Módulo F)."""

from algoritmos.divide_conquista import merge_sort


def nodos_por_grado(grafo, limite=None):
    """Lista [(nodo, grado)] ordenada de mayor a menor grado (desempate por id).

    Usa el Merge Sort propio del proyecto. Tiempo O(n log n).
    """
    pares = merge_sort([(-grafo.grado(n), n) for n in grafo.nodos()])
    resultado = [(n, -g) for g, n in pares]
    return resultado if limite is None else resultado[:limite]


def celdas_representaciones(n, m, dirigido):
    """Número de celdas que usa cada representación (modelo teórico simple).

    Lista de adyacencia: n cabeceras + entradas (m si es dirigido, 2m si no) -> O(n + m).
    Matriz de adyacencia: n * n celdas -> O(n^2).
    """
    entradas = m if dirigido else 2 * m
    return {"lista": n + entradas, "matriz": n * n}


def comparar_representaciones(grafo):
    """Compara el tamaño de ambas representaciones para el grafo dado."""
    n, m = grafo.num_nodos, grafo.num_conexiones
    celdas = celdas_representaciones(n, m, grafo.dirigido)
    maximo = n * (n - 1) if grafo.dirigido else n * (n - 1) // 2
    return {
        "nodos": n,
        "conexiones": m,
        "celdas_lista": celdas["lista"],
        "celdas_matriz": celdas["matriz"],
        "densidad": (m / maximo) if maximo else 0.0,
    }


def crecimiento_representaciones(tamanos, conexiones_por_nodo=2, dirigido=False):
    """Calcula el tamaño teórico de ambas representaciones al crecer n.

    Se supone m = conexiones_por_nodo * n (grafo disperso). Son valores calculados
    con las fórmulas anteriores, NO mediciones de memoria del programa.
    """
    if conexiones_por_nodo < 0:
        raise ValueError("conexiones_por_nodo no puede ser negativo.")
    filas = []
    for n in tamanos:
        if n < 0:
            raise ValueError("Los tamaños no pueden ser negativos.")
        m = conexiones_por_nodo * n
        celdas = celdas_representaciones(n, m, dirigido)
        filas.append({"nodos": n, "conexiones": m,
                      "celdas_lista": celdas["lista"], "celdas_matriz": celdas["matriz"]})
    return filas
