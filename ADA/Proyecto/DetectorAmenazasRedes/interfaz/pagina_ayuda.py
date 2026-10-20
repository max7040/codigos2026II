"""Página: Ayuda y documentación."""

import streamlit as st


def mostrar():
    st.title("📖 Ayuda y documentación")
    st.markdown("""
**Qué es:** una aplicación educativa que modela una red simulada como grafo y marca patrones
sospechosos con reglas explicables. No escanea redes reales ni usa inteligencia artificial.

**Flujo recomendado**
1. *Constructor de redes*: edita o importa la red (JSON o CSV).
2. *Visualización del grafo*: observa la red (NetworkX calcula posiciones, Plotly dibuja).
3. *Detector de amenazas*: ajusta umbrales y revisa cada alerta y su justificación.
4. *Laboratorio de algoritmos*: prueba cada algoritmo de la unidad.
5. *Estadísticas y comparaciones*: gráficos y experimentos de ordenamiento.

**Formatos de importación**
- JSON: `{"dirigido": true, "nodos": [{"id": "pc-01", "tipo": "equipo"}], "conexiones": [{"origen": "pc-01", "destino": "srv-web", "peso": 1, "frecuencia": 30, "eventos": 12}]}`
- CSV de nodos: `id,tipo` · CSV de conexiones: `origen,destino,peso,frecuencia,eventos`.
- Tipos válidos: equipo, servidor, cuenta.

**Aviso:** las alertas son ejemplos educativos, no pruebas definitivas de una amenaza.
""")
