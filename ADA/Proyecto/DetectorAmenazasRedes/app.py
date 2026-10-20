"""Detector de Amenazas en Redes — punto de entrada de Streamlit.

Ejecutar con:  streamlit run app.py
Aquí solo se configura la página y se elige qué pantalla mostrar; la lógica está
en los paquetes `interfaz/`, `analisis/`, `algoritmos/`, `estructuras/` y `visualizacion/`.
"""

import streamlit as st

st.set_page_config(page_title="Detector de Amenazas en Redes", page_icon="🛡️", layout="wide")

from interfaz import (estado, pagina_ayuda, pagina_constructor, pagina_detector,  # noqa: E402
                      pagina_estadisticas, pagina_inicio, pagina_laboratorio,
                      pagina_visualizacion)

PAGINAS = {
    "🏠 Inicio": pagina_inicio,
    "🧱 Constructor de redes": pagina_constructor,
    "🕸️ Visualización del grafo": pagina_visualizacion,
    "🚨 Detector de amenazas": pagina_detector,
    "🧪 Laboratorio de algoritmos": pagina_laboratorio,
    "📊 Estadísticas y comparaciones": pagina_estadisticas,
    "📖 Ayuda y documentación": pagina_ayuda,
}

estado.inicializar()
with st.sidebar:
    st.header("Menú")
    seleccion = st.radio("Sección", list(PAGINAS), label_visibility="collapsed")
    st.caption("Proyecto académico. Datos simulados.")
PAGINAS[seleccion].mostrar()
