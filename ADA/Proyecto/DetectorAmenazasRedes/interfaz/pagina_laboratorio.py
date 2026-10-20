"""Página: Laboratorio de algoritmos (Módulo E y F)."""

import streamlit as st

from algoritmos.busqueda import busqueda_binaria, busqueda_binaria_recursiva, busqueda_lineal
from algoritmos.divide_conquista import merge_sort, quick_sort
from algoritmos.ordenamiento import burbuja, insercion, seleccion
from algoritmos.programacion_dinamica import cadena_matrices, mochila_01
from algoritmos.recursion import (LIMITE_FIBONACCI_RECURSIVO, factorial_iterativo,
                                  factorial_recursivo, fibonacci_iterativo, fibonacci_memoizado,
                                  fibonacci_recursivo, fibonacci_tabulacion)
from algoritmos.voraces import mochila_fraccionaria, seleccion_actividades
from analisis.metricas_grafo import comparar_representaciones
from estructuras.arbol_binario import ArbolBinarioBusqueda
from estructuras.tabla_hash import TablaHash
from interfaz import estado

ORDENAMIENTOS = {
    "Burbuja": (burbuja, "Compara pares adyacentes y los intercambia.", "O(n²) (mejor caso O(n))", "O(1)"),
    "Inserción": (insercion, "Inserta cada elemento en su lugar dentro de la parte ya ordenada.",
                  "O(n²) (mejor caso O(n))", "O(1)"),
    "Selección": (seleccion, "Selecciona el mínimo restante y lo coloca al inicio.", "O(n²)", "O(1)"),
    "Merge Sort": (merge_sort, "Divide la lista, ordena cada mitad y las mezcla.", "O(n log n)", "O(n)"),
    "Quick Sort": (quick_sort, "Elige un pivote y particiona; ordena cada parte.",
                   "O(n log n) promedio, O(n²) peor caso", "O(log n) promedio"),
}


def _numeros(texto):
    """Convierte '5, 3, 8' en [5.0, 3.0, 8.0] (enteros si es posible). Lanza ValueError."""
    partes = [p for p in texto.replace(";", ",").replace("\n", ",").split(",") if p.strip()]
    valores = []
    for p in partes:
        x = float(p)
        valores.append(int(x) if x == int(x) else x)
    return valores


def _sec_ordenamiento():
    st.write("**Objetivo:** ordenar una lista de menor a mayor (implementaciones propias, sin `sorted`).")
    texto = st.text_input("Lista (separada por comas)", "64, 25, 12, 22, 11, 25")
    nombre = st.selectbox("Algoritmo", list(ORDENAMIENTOS))
    try:
        datos = _numeros(texto)
    except ValueError:
        st.error("Escribe solo números separados por comas.")
        return
    funcion, idea, tiempo, espacio = ORDENAMIENTOS[nombre]
    st.code(f"entrada : {datos}\nresultado: {funcion(datos)}")
    st.markdown(f"**Funcionamiento:** {idea}  \n**Tiempo:** {tiempo} · **Espacio:** {espacio}  \n"
                "**Aplicación:** el detector ordena sus alertas y los nodos por grado con Merge Sort.")


def _sec_busqueda():
    st.write("**Objetivo:** hallar el índice de un valor (−1 si no está).")
    texto = st.text_input("Lista (separada por comas)", "3, 8, 12, 19, 25, 31")
    objetivo = st.text_input("Valor buscado", "19")
    try:
        datos, buscado = _numeros(texto), _numeros(objetivo)[0]
    except (ValueError, IndexError):
        st.error("Escribe números válidos.")
        return
    ordenados = merge_sort(datos)
    st.code(f"lineal                : {busqueda_lineal(datos, buscado)}  (sobre la lista tal cual)\n"
            f"binaria (iterativa)   : {busqueda_binaria(ordenados, buscado)}  (sobre {ordenados})\n"
            f"binaria (recursiva)   : {busqueda_binaria_recursiva(ordenados, buscado)}")
    st.markdown("**Complejidad:** lineal O(n); binaria O(log n) pero exige lista ordenada. "
                "Espacio: O(1) (la recursiva O(log n)).")


def _sec_tabla_hash():
    st.write("**Objetivo:** guardar y buscar pares clave-valor en O(1) promedio, con "
             "encadenamiento para las colisiones.")
    claves = st.text_input("Claves (separadas por comas)", "pc-01, pc-02, srv-web, cta-admin, pc-03")
    capacidad = st.slider("Capacidad inicial", 1, 16, 4)
    tabla = TablaHash(capacidad)
    for i, c in enumerate(k.strip() for k in claves.split(",") if k.strip()):
        tabla.insertar(c, i)
    st.json(tabla.estadisticas())
    st.markdown("Una **cadena máxima** mayor que 1 indica colisiones. La tabla se redimensiona "
                "cuando el factor de carga supera 0,75. **Aplicación:** índice rápido de nodos.")


def _sec_arbol():
    st.write("**Objetivo:** almacenar claves ordenadas con inserción y búsqueda O(h).")
    texto = st.text_input("Claves", "50, 30, 70, 20, 40, 60, 80")
    buscada = st.text_input("Clave a buscar", "60")
    try:
        claves, k = _numeros(texto), _numeros(buscada)[0]
    except (ValueError, IndexError):
        st.error("Escribe números válidos.")
        return
    arbol = ArbolBinarioBusqueda()
    for c in claves:
        arbol.insertar(c)
    st.code(f"inorden : {list(arbol.inorden())}\naltura  : {arbol.altura()}\n"
            f"¿contiene {k}? {bool(arbol.buscar(k))}")
    st.markdown("**Complejidad:** O(log n) si está equilibrado, O(n) en el peor caso.")


def _sec_recursion():
    st.write("**Objetivo:** comparar enfoques recursivo, iterativo y dinámico.")
    n = st.number_input("n", min_value=0, max_value=500, value=20, step=1)
    n = int(n)
    st.code(f"factorial recursivo : {factorial_recursivo(n) if n <= 500 else '-'}\n"
            f"factorial iterativo : {factorial_iterativo(n)}")
    filas = []
    for nombre, f, comp in (("Recursivo", fibonacci_recursivo, "≈ O(2ⁿ)"),
                            ("Iterativo", fibonacci_iterativo, "O(n)"),
                            ("Memoización", fibonacci_memoizado, "O(n)"),
                            ("Tabulación", fibonacci_tabulacion, "O(n)")):
        try:
            filas.append({"enfoque": nombre, "F(n)": str(f(n)), "tiempo": comp})
        except ValueError as e:
            filas.append({"enfoque": nombre, "F(n)": f"no calculado: {e}", "tiempo": comp})
        except RecursionError:
            filas.append({"enfoque": nombre, "F(n)": "n demasiado grande para la pila", "tiempo": comp})
    st.dataframe(filas, hide_index=True, use_container_width=True)
    st.caption(f"La versión recursiva simple se limita a n ≤ {LIMITE_FIBONACCI_RECURSIVO} para no bloquear la app.")


def _sec_voraces():
    st.write("**Objetivo:** tomar la mejor opción local en cada paso.")
    elementos = [("A", 60, 10), ("B", 100, 20), ("C", 120, 30)]
    cap = st.number_input("Capacidad de la mochila", min_value=0, value=50)
    valor, tomados = mochila_fraccionaria(elementos, cap)
    st.write("Mochila fraccionaria con elementos (nombre, valor, peso):", elementos)
    st.code(f"valor total = {valor:g}\ntomados     = {tomados}")
    acts = [("Reunión", 1, 4), ("Backup", 3, 5), ("Escaneo", 0, 6), ("Revisión", 5, 7), ("Informe", 5, 9)]
    st.write("Selección de actividades (nombre, inicio, fin):", acts)
    st.code(f"elegidas = {seleccion_actividades(acts)}")
    st.markdown("**Complejidad:** O(n log n) por el ordenamiento. **Aplicación:** priorizar tareas de revisión.")


def _sec_pd():
    st.write("**Objetivo:** resolver subproblemas una sola vez guardando resultados en una tabla.")
    elementos = [("A", 60, 10), ("B", 100, 20), ("C", 120, 30)]
    cap = st.number_input("Capacidad (entera)", min_value=0, value=50, key="cap_pd")
    st.code(f"mochila 0/1 {elementos} -> {mochila_01(elementos, int(cap))}")
    dims = st.text_input("Dimensiones de la cadena de matrices", "10, 30, 5, 60")
    try:
        st.code(f"cadena de matrices {dims} -> {cadena_matrices(_numeros(dims))}")
    except ValueError as e:
        st.error(str(e))
    st.markdown("**Complejidad:** mochila O(n·W) tiempo y espacio; cadena de matrices O(n³) tiempo y O(n²) espacio.")


def _sec_grafos():
    grafo = estado.grafo()
    st.write("**Objetivo:** consultar vecinos, grados y comparar las representaciones.")
    if grafo.num_nodos == 0:
        st.info("La red está vacía.")
        return
    nodo = st.selectbox("Nodo", grafo.nodos())
    st.code(f"vecinos      : {grafo.vecinos(nodo)}\npredecesores : {grafo.predecesores(nodo)}\n"
            f"grado        : {grafo.grado(nodo)}")
    st.json(comparar_representaciones(grafo))
    with st.expander("Lista de adyacencia"):
        st.json(grafo.lista_adyacencia())
    with st.expander("Matriz de adyacencia"):
        nodos, matriz = grafo.matriz_adyacencia()
        st.dataframe({n: [fila[j] for fila in matriz] for j, n in enumerate(nodos)},
                     use_container_width=True)
    st.markdown("**Lista:** O(n+m) espacio, vecinos en O(g). **Matriz:** O(n²) espacio, ¿existe arista? en O(1).")


SECCIONES = {
    "Ordenamiento": _sec_ordenamiento, "Búsqueda": _sec_busqueda, "Tabla hash": _sec_tabla_hash,
    "Árbol binario de búsqueda": _sec_arbol, "Recursividad y Fibonacci": _sec_recursion,
    "Algoritmos voraces": _sec_voraces, "Programación dinámica": _sec_pd,
    "Grafos: listas y matrices": _sec_grafos,
}


def mostrar():
    st.title("🧪 Laboratorio de algoritmos")
    seccion = st.selectbox("Tema", list(SECCIONES))
    SECCIONES[seccion]()
