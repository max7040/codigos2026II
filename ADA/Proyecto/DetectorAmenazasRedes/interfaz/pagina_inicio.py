"""Página: Inicio (Módulo A, panel principal)."""

import streamlit as st

from analisis.detector import detectar, resumen_por_nivel
from interfaz import estado
from visualizacion.estadisticas import grafico_alertas_por_nivel


def mostrar():
    st.title("🛡️ Detector de Amenazas en Redes")
    st.caption("Proyecto académico — Análisis y Diseño de Algoritmos (Unidad 1). "
               "Trabaja solo con redes simuladas: no escanea ni ataca equipos reales.")
    grafo = estado.grafo()
    alertas = detectar(grafo, st.session_state.config)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nodos", grafo.num_nodos)
    c2.metric("Conexiones", grafo.num_conexiones)
    c3.metric("Eventos registrados", grafo.total_eventos())
    c4.metric("Alertas generadas", len(alertas))

    st.subheader("Distribución de niveles de riesgo")
    resumen = resumen_por_nivel(alertas)
    if alertas:
        st.plotly_chart(grafico_alertas_por_nivel(resumen), use_container_width=True)
    else:
        st.info("No hay alertas con la configuración actual.")
    st.markdown(
        f"**Tipo de red:** {'dirigida' if grafo.dirigido else 'no dirigida'}. "
        "Las alertas se calculan con reglas explicables (sin inteligencia artificial) "
        "y no son prueba de una amenaza real."
    )
    st.markdown(
        "**¿Por dónde empezar?** Usa el menú lateral: *Constructor de redes* para editar la red, "
        "*Visualización del grafo* para verla, *Detector de amenazas* para ver las alertas y "
        "*Laboratorio de algoritmos* para probar los algoritmos de la unidad."
    )
