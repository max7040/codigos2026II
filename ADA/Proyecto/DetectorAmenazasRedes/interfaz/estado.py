"""Estado compartido de la aplicación (st.session_state)."""

from pathlib import Path

import streamlit as st

from analisis.detector import ConfigDetector
from utils.validaciones import importar_json

RUTA_EJEMPLO = Path(__file__).resolve().parent.parent / "data" / "ejemplo_red.json"


def inicializar():
    """Carga la red de ejemplo y la configuración por defecto la primera vez."""
    if "grafo" not in st.session_state:
        st.session_state.grafo = importar_json(RUTA_EJEMPLO.read_text(encoding="utf-8"))
    if "config" not in st.session_state:
        st.session_state.config = ConfigDetector()
    if "benchmark" not in st.session_state:
        st.session_state.benchmark = None


def grafo():
    return st.session_state.grafo


def reemplazar_grafo(nuevo):
    st.session_state.grafo = nuevo
