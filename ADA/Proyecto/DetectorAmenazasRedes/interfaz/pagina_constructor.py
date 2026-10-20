"""Página: Constructor de redes (Módulo B)."""

import streamlit as st

from estructuras.grafo import ErrorGrafo, Grafo, TIPOS_NODO
from interfaz import estado
from utils.validaciones import (ErrorValidacion, exportar_csv, exportar_json,
                                importar_csv, importar_json)


def _mostrar_errores(e):
    st.error("No se pudo importar la red. Corrige lo siguiente:")
    for linea in getattr(e, "errores", [str(e)]):
        st.markdown(f"- {linea}")


def _tab_nodos(grafo):
    st.markdown("#### Agregar nodo")
    with st.form("form_nodo", clear_on_submit=True):
        id_nodo = st.text_input("Identificador", placeholder="ej. pc-06")
        tipo = st.selectbox("Tipo", TIPOS_NODO)
        if st.form_submit_button("Agregar nodo"):
            try:
                grafo.agregar_nodo(id_nodo.strip(), tipo)
                st.success(f"Nodo «{id_nodo.strip()}» agregado.")
            except ErrorGrafo as e:
                st.error(str(e))
    if grafo.num_nodos:
        st.markdown("#### Editar o eliminar nodo")
        nodo = st.selectbox("Nodo", grafo.nodos(), key="sel_nodo")
        col1, col2 = st.columns(2)
        nuevo_tipo = col1.selectbox("Nuevo tipo", TIPOS_NODO,
                                    index=TIPOS_NODO.index(grafo.tipo_nodo(nodo)), key=f"tipo_edit_{nodo}")
        if col1.button("Guardar tipo"):
            try:
                grafo.editar_nodo(nodo, nuevo_tipo)
                st.success("Tipo actualizado.")
            except ErrorGrafo as e:
                st.error(str(e))
        col2.write("Eliminar un nodo también elimina sus conexiones.")
        if col2.button("Eliminar nodo", type="primary"):
            try:
                grafo.eliminar_nodo(nodo)
                st.success(f"Nodo «{nodo}» eliminado.")
                st.rerun()
            except ErrorGrafo as e:
                st.error(str(e))
    st.dataframe([{"id": n, "tipo": grafo.tipo_nodo(n), "grado": grafo.grado(n)}
                  for n in grafo.nodos()], use_container_width=True, hide_index=True)


def _tab_conexiones(grafo):
    nodos = grafo.nodos()
    if len(nodos) < 2:
        st.info("Necesitas al menos dos nodos para crear conexiones.")
    else:
        st.markdown("#### Agregar conexión")
        with st.form("form_conexion", clear_on_submit=False):
            c1, c2 = st.columns(2)
            origen = c1.selectbox("Origen", nodos)
            destino = c2.selectbox("Destino", nodos, index=1)
            c3, c4, c5 = st.columns(3)
            peso = c3.number_input("Peso (> 0)", min_value=0.0, value=1.0, step=0.5)
            frecuencia = c4.number_input("Frecuencia (≥ 0)", min_value=0.0, value=0.0, step=5.0)
            eventos = c5.number_input("Eventos (≥ 0)", min_value=0, value=0, step=1)
            if st.form_submit_button("Agregar conexión"):
                try:
                    grafo.agregar_conexion(origen, destino, peso, frecuencia, int(eventos))
                    st.success(f"Conexión {origen} → {destino} agregada.")
                except ErrorGrafo as e:
                    st.error(str(e))
    conexiones = grafo.conexiones()
    if conexiones:
        st.markdown("#### Editar o eliminar conexión")
        etiquetas = [f"{c['origen']} → {c['destino']}" for c in conexiones]
        i = st.selectbox("Conexión", range(len(conexiones)), format_func=lambda k: etiquetas[k])
        c = conexiones[i]
        c1, c2, c3 = st.columns(3)
        peso = c1.number_input("Peso", min_value=0.0, value=float(c["peso"]), key=f"e_peso_{etiquetas[i]}")
        frecuencia = c2.number_input("Frecuencia", min_value=0.0, value=float(c["frecuencia"]), key=f"e_frec_{etiquetas[i]}")
        eventos = c3.number_input("Eventos", min_value=0, value=int(c["eventos"]), key=f"e_even_{etiquetas[i]}")
        b1, b2 = st.columns(2)
        if b1.button("Guardar cambios"):
            try:
                grafo.editar_conexion(c["origen"], c["destino"], peso, frecuencia, int(eventos))
                st.success("Conexión actualizada.")
            except ErrorGrafo as e:
                st.error(str(e))
        if b2.button("Eliminar conexión", type="primary"):
            try:
                grafo.eliminar_conexion(c["origen"], c["destino"])
                st.success("Conexión eliminada.")
                st.rerun()
            except ErrorGrafo as e:
                st.error(str(e))
    st.dataframe(grafo.conexiones(), use_container_width=True, hide_index=True)


def _tab_importar_exportar(grafo):
    st.markdown("#### Exportar")
    nodos_csv, conexiones_csv = exportar_csv(grafo)
    c1, c2, c3 = st.columns(3)
    c1.download_button("Descargar JSON", exportar_json(grafo), "red.json", "application/json")
    c2.download_button("CSV de nodos", nodos_csv, "nodos.csv", "text/csv")
    c3.download_button("CSV de conexiones", conexiones_csv, "conexiones.csv", "text/csv")

    st.markdown("#### Importar JSON")
    archivo = st.file_uploader("Archivo JSON", type="json", key="up_json")
    if archivo is not None and st.button("Importar JSON"):
        try:
            estado.reemplazar_grafo(importar_json(archivo.getvalue().decode("utf-8-sig")))
            st.success("Red importada correctamente.")
            st.rerun()
        except (ErrorValidacion, UnicodeDecodeError) as e:
            _mostrar_errores(e)

    st.markdown("#### Importar CSV (dos archivos)")
    dirigido = st.checkbox("La red importada es dirigida", value=False)
    a_nodos = st.file_uploader("CSV de nodos (id,tipo)", type="csv", key="up_n")
    a_con = st.file_uploader("CSV de conexiones (origen,destino,peso,frecuencia,eventos)",
                             type="csv", key="up_c")
    if a_nodos and a_con and st.button("Importar CSV"):
        try:
            estado.reemplazar_grafo(importar_csv(a_nodos.getvalue().decode("utf-8-sig"),
                                                 a_con.getvalue().decode("utf-8-sig"), dirigido))
            st.success("Red importada correctamente.")
            st.rerun()
        except (ErrorValidacion, UnicodeDecodeError) as e:
            _mostrar_errores(e)


def _tab_nueva():
    st.markdown("#### Empezar de cero o restaurar el ejemplo")
    dirigido = st.radio("Tipo de red nueva", ["Dirigida", "No dirigida"], horizontal=True)
    c1, c2 = st.columns(2)
    if c1.button("Crear red vacía"):
        estado.reemplazar_grafo(Grafo(dirigido == "Dirigida"))
        st.rerun()
    if c2.button("Restaurar red de ejemplo"):
        estado.reemplazar_grafo(importar_json(estado.RUTA_EJEMPLO.read_text(encoding="utf-8")))
        st.rerun()


def mostrar():
    st.title("🧱 Constructor de redes")
    grafo = estado.grafo()
    st.caption(f"Red actual: {'dirigida' if grafo.dirigido else 'no dirigida'} · "
               f"{grafo.num_nodos} nodos · {grafo.num_conexiones} conexiones")
    t1, t2, t3, t4 = st.tabs(["Nodos", "Conexiones", "Importar / Exportar", "Nueva red"])
    with t1:
        _tab_nodos(grafo)
    with t2:
        _tab_conexiones(grafo)
    with t3:
        _tab_importar_exportar(grafo)
    with t4:
        _tab_nueva()
