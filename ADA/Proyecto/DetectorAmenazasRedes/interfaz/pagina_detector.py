"""Página: Detector de amenazas simuladas (Módulo D)."""

import streamlit as st

from analisis.detector import REGLAS, ConfigDetector, detectar
from interfaz import estado


def mostrar():
    st.title("🚨 Detector de amenazas simuladas")
    st.caption("Reglas configurables y explicables. No usa IA y sus resultados no prueban "
               "una amenaza real: son un ejercicio educativo.")
    cfg = st.session_state.config
    with st.expander("⚙️ Configurar reglas y umbrales", expanded=False):
        c1, c2 = st.columns(2)
        umbral_grado = c1.number_input("Umbral de grado (conexiones)", min_value=1,
                                       value=int(cfg.umbral_grado))
        umbral_frecuencia = c2.number_input("Umbral de frecuencia", min_value=1.0,
                                            value=float(cfg.umbral_frecuencia))
        umbral_eventos = c1.number_input("Umbral de eventos por conexión", min_value=1,
                                         value=int(cfg.umbral_eventos))
        umbral_servidores = c2.number_input("Umbral de servidores por cuenta", min_value=1,
                                            value=int(cfg.umbral_servidores))
        activas = st.multiselect("Reglas activas", list(REGLAS),
                                 default=[r for r in REGLAS if r in cfg.reglas_activas],
                                 format_func=lambda r: REGLAS[r]["nombre"])
        try:
            nueva = ConfigDetector(umbral_grado=umbral_grado, umbral_frecuencia=umbral_frecuencia,
                                   umbral_eventos=umbral_eventos, umbral_servidores=umbral_servidores,
                                   reglas_activas=frozenset(activas))
            nueva.validar()
            st.session_state.config = nueva
        except ValueError as e:
            st.error(str(e))

    alertas = detectar(estado.grafo(), st.session_state.config)
    st.metric("Alertas generadas", len(alertas))
    if not alertas:
        st.success("No se activó ninguna regla con la configuración actual.")
        return
    niveles = sorted({a.nivel for a in alertas})
    filtro = st.multiselect("Filtrar por nivel", niveles, default=niveles)
    st.dataframe([{k: a.a_dict()[k] for k in ("id", "nivel", "puntaje", "nombre_regla", "objetivo",
                                              "valor", "umbral")}
                  for a in alertas if a.nivel in filtro], use_container_width=True, hide_index=True)
    st.subheader("Detalle de cada alerta")
    for a in alertas:
        if a.nivel not in filtro:
            continue
        with st.expander(f"{a.id_alerta} · {a.nivel} ({a.puntaje}) · {a.descripcion_objetivo} · {a.nombre_regla}"):
            st.markdown(f"**Objetivo:** {a.tipo_objetivo} `{a.descripcion_objetivo}`")
            st.markdown(f"**Regla activada:** {a.nombre_regla}")
            st.markdown(f"**Justificación:** {a.explicacion}")
            st.json(a.datos)
            st.markdown(f"**Riesgo:** {a.puntaje}/100 → {a.nivel}")
            st.markdown(f"**Recomendación defensiva:** {a.recomendacion}")
    with st.expander("¿Cómo se calcula el riesgo?"):
        st.markdown("Razón = valor observado ÷ umbral. Puntaje = min(100, round(50 × razón)). "
                    "La regla se activa si valor ≥ umbral. Niveles: Bajo [50,60), Medio [60,80), "
                    "Alto [80,100), Crítico = 100 (valor ≥ 2 × umbral).")
