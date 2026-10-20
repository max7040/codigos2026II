"""Página: Estadísticas y comparaciones (Módulos G y H)."""

import streamlit as st

from analisis.benchmark import ALGORITMOS, TIPOS_DATOS, ejecutar_benchmark
from analisis.detector import detectar, resumen_por_nivel
from analisis.metricas_grafo import crecimiento_representaciones, nodos_por_grado
from interfaz import estado
from visualizacion import estadisticas as graficos


def _tab_red(grafo):
    if grafo.num_nodos == 0:
        st.info("La red está vacía.")
        return
    st.plotly_chart(graficos.grafico_nodos_por_grado(nodos_por_grado(grafo, 10)), use_container_width=True)
    st.caption("Cómo leerlo: barras largas = nodos muy conectados (posibles puntos de concentración).")
    if grafo.num_conexiones:
        st.plotly_chart(graficos.grafico_eventos_por_conexion(grafo.conexiones()), use_container_width=True)
        st.caption("Eventos simulados por conexión: las más altas son candidatas a la regla de repetición.")
    alertas = detectar(grafo, st.session_state.config)
    st.plotly_chart(graficos.grafico_alertas_por_nivel(resumen_por_nivel(alertas)), use_container_width=True)


def _tab_representaciones():
    maximo = st.slider("Nodos máximos", 10, 500, 100, step=10)
    por_nodo = st.slider("Conexiones por nodo (red dispersa)", 1, 10, 2)
    tamanos = list(range(10, maximo + 1, 10))
    filas = crecimiento_representaciones(tamanos, por_nodo, estado.grafo().dirigido)
    st.plotly_chart(graficos.grafico_comparacion_representaciones(filas), use_container_width=True)
    st.caption("Son valores calculados con fórmulas (lista ≈ n+m, matriz = n²), no mediciones de memoria.")


def _tab_benchmark():
    st.write("Experimento reproducible: mismos datos (semilla fija) para cada algoritmo, copias "
             "equivalentes, `time.perf_counter()` y verificación del resultado.")
    nombres = st.multiselect("Algoritmos", list(ALGORITMOS), default=list(ALGORITMOS))
    tamanos_txt = st.text_input("Tamaños de entrada", "100, 500, 1000")
    tipos = st.multiselect("Tipos de datos", TIPOS_DATOS, default=["aleatorio"])
    repeticiones = st.slider("Repeticiones", 1, 10, 3)
    if st.button("Ejecutar experimento", type="primary"):
        try:
            tamanos = [int(t) for t in tamanos_txt.split(",") if t.strip()]
            if not tamanos or any(t < 1 or t > 5000 for t in tamanos):
                raise ValueError
        except ValueError:
            st.error("Escribe enteros entre 1 y 5000 separados por comas.")
            return
        if not nombres or not tipos:
            st.error("Elige al menos un algoritmo y un tipo de datos.")
            return
        with st.spinner("Midiendo..."):
            st.session_state.benchmark = ejecutar_benchmark(nombres, tamanos, tipos, repeticiones)
    registros = st.session_state.benchmark
    if not registros:
        st.info("Aún no hay mediciones. Pulsa «Ejecutar experimento».")
        return
    if not all(r["correcto"] for r in registros):
        st.error("Algún algoritmo devolvió un resultado incorrecto.")
    else:
        st.success("Todos los resultados fueron verificados como correctos.")
    st.dataframe(registros, hide_index=True, use_container_width=True)
    log = st.checkbox("Escala logarítmica en el eje Y")
    for tipo in sorted({r["tipo"] for r in registros}):
        st.plotly_chart(graficos.grafico_benchmark(registros, tipo, log), use_container_width=True)
    st.caption("Estos tiempos dependen de tu equipo, del tamaño y de la implementación; no son la "
               "complejidad teórica ni prueban que un algoritmo sea siempre más rápido.")


def mostrar():
    st.title("📊 Estadísticas y comparaciones")
    t1, t2, t3 = st.tabs(["Red y alertas", "Representaciones", "Comparación de ordenamientos"])
    with t1:
        _tab_red(estado.grafo())
    with t2:
        _tab_representaciones()
    with t3:
        _tab_benchmark()
