"""Página: Visualización del grafo (Módulo C)."""

import streamlit as st

from analisis.detector import detectar
from interfaz import estado
from visualizacion.grafo_visual import LAYOUTS, construir_figura


def mostrar():
    st.title("🕸️ Visualización del grafo")
    grafo = estado.grafo()
    c1, c2, c3 = st.columns(3)
    layout = c1.selectbox("Distribución", LAYOUTS)
    mostrar_pesos = c2.checkbox("Mostrar pesos", value=True)
    resaltar = c3.checkbox("Resaltar alertas", value=True)
    alertas = detectar(grafo, st.session_state.config) if resaltar else []
    st.plotly_chart(construir_figura(grafo, alertas, layout, mostrar_pesos),
                    use_container_width=True)
    with st.expander("¿Cómo se relaciona el dato con el dibujo?"):
        st.markdown(
            "1. Tu red vive en el objeto `Grafo` (lista de adyacencia propia).\n"
            "2. `a_networkx` la convierte en un grafo de **NetworkX**, que calcula las "
            "posiciones (x, y) según la distribución elegida.\n"
            "3. **Plotly** dibuja con esas posiciones: un trazo por tipo de nodo, líneas para "
            "las conexiones y borde/línea roja para lo que tiene alertas.\n"
            "4. El tamaño del nodo crece con su grado. Pasa el cursor sobre nodos y puntos "
            "medios de las conexiones para ver sus datos."
        )
