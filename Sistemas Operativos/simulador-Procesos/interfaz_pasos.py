"""
interfaz_pasos.py
Ventana de la simulación paso a paso.
Solo muestra los pasos que ya registró el simulador: no contiene lógica
de planificación.
"""

import tkinter as tk
from tkinter import ttk

import gantt
import simulador

COLUMNAS_LISTOS = ("Proceso", "Restante", "Prioridad", "Llegada", "Estado")
COLUMNAS_RESULTADOS = ("ID", "Llegada", "Ejecución", "Prioridad", "Inicio",
                       "Finalización (CT)", "Retorno (TAT)", "Espera (WT)",
                       "Respuesta (RT)")


class VentanaPasoAPaso:
    def __init__(self, raiz, simulacion):
        self.simulacion = simulacion
        self.indice = 0                      # paso que se está mostrando

        self.ventana = tk.Toplevel(raiz)
        self.ventana.title("Simulación paso a paso")
        self.ventana.geometry("1250x820")
        self.ventana.minsize(1100, 700)
        try:
            self.ventana.state("zoomed")     # maximizada en Windows
        except tk.TclError:
            pass

        # El orden importa: lo que se empaqueta abajo primero queda más abajo
        self._crear_encabezado()
        self._crear_resultados()
        self._crear_botones()
        self._crear_cuerpo()

        self.ventana.bind("<Right>", lambda evento: self.siguiente())
        self.ventana.bind("<Left>", lambda evento: self.anterior())

        self._mostrar_paso()

    # ======================================================================
    # Construcción de la ventana
    # ======================================================================
    def _crear_encabezado(self):
        sim = self.simulacion
        texto = f"Algoritmo: {sim.algoritmo} ({simulador.TIPOS[sim.algoritmo]})"
        if sim.quantum is not None:
            texto += f"  |  Quantum = {sim.quantum}"

        marco = ttk.Frame(self.ventana, padding=(10, 6))
        marco.pack(fill="x")
        ttk.Label(marco, text="SIMULACIÓN PASO A PASO", style="Titulo.TLabel",
                  anchor="center").pack(fill="x")
        ttk.Label(marco, text=texto, style="Tipo.TLabel",
                  anchor="center").pack(fill="x")

        self.var_paso = tk.StringVar()
        self.var_tiempo = tk.StringVar()
        self.var_evento = tk.StringVar()
        fila = ttk.Frame(marco)
        fila.pack(pady=(4, 0))
        for variable in (self.var_paso, self.var_tiempo, self.var_evento):
            ttk.Label(fila, textvariable=variable, style="Valor.TLabel").pack(
                side="left", padx=18)

    def _crear_resultados(self):
        marco = ttk.LabelFrame(self.ventana, padding=6,
                               text="RESULTADOS (se completan en el último paso)")
        marco.pack(side="bottom", fill="x", padx=10, pady=(0, 6))

        self.tabla_resultados = ttk.Treeview(
            marco, columns=COLUMNAS_RESULTADOS, show="headings", height=5,
            selectmode="none")
        anchos = (70, 70, 80, 75, 65, 120, 100, 95, 110)
        for columna, ancho in zip(COLUMNAS_RESULTADOS, anchos):
            self.tabla_resultados.heading(columna, text=columna)
            self.tabla_resultados.column(columna, width=ancho, anchor="center")
        self.tabla_resultados.pack(fill="x")

        self.var_prom_espera = tk.StringVar(value="-")
        self.var_prom_retorno = tk.StringVar(value="-")
        self.var_prom_respuesta = tk.StringVar(value="-")
        self.var_tiempo_total = tk.StringVar(value="-")
        self.var_utilizacion = tk.StringVar(value="-")
        self.var_cpu = tk.StringVar(value="-")
        self.var_completados = tk.StringVar(value="-")

        estadisticas = [
            ("Promedio de espera (WT):", self.var_prom_espera),
            ("Promedio de retorno (TAT):", self.var_prom_retorno),
            ("Promedio de respuesta (RT):", self.var_prom_respuesta),
            ("Tiempo total:", self.var_tiempo_total),
            ("Utilización de CPU:", self.var_utilizacion),
            ("CPU ocupada / inactiva:", self.var_cpu),
            ("Procesos completados:", self.var_completados),
        ]
        cuadro = ttk.Frame(marco)
        cuadro.pack(fill="x", pady=(6, 0))
        for i, (texto, variable) in enumerate(estadisticas):
            fila = i // 4
            columna = (i % 4) * 2
            ttk.Label(cuadro, text=texto).grid(row=fila, column=columna,
                                               sticky="w", padx=(0, 4), pady=1)
            ttk.Label(cuadro, textvariable=variable, style="Valor.TLabel").grid(
                row=fila, column=columna + 1, sticky="w", padx=(0, 24), pady=1)
    def _crear_botones(self):
        marco = ttk.Frame(self.ventana, padding=(10, 6))
        marco.pack(side="bottom", fill="x")
        centro = ttk.Frame(marco)
        centro.pack()

        self.boton_anterior = ttk.Button(centro, text="← Anterior",
                                         style="Accion.TButton", command=self.anterior)
        self.boton_siguiente = ttk.Button(centro, text="Siguiente →",
                                          style="Accion.TButton", command=self.siguiente)
        self.boton_reiniciar = ttk.Button(centro, text="Reiniciar simulación",
                                          style="Accion.TButton", command=self.reiniciar)
        self.boton_anterior.pack(side="left", padx=6)
        self.boton_siguiente.pack(side="left", padx=6)
        self.boton_reiniciar.pack(side="left", padx=6)

    def _crear_cuerpo(self):
        cuerpo = ttk.Frame(self.ventana, padding=(10, 0))
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        izquierda = ttk.Frame(cuerpo)
        izquierda.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        derecha = ttk.Frame(cuerpo)
        derecha.grid(row=0, column=1, sticky="nsew")

        self._crear_panel_cpu(izquierda)
        self._crear_panel_listos(izquierda)
        self._crear_panel_estado(izquierda)
        self._crear_panel_decision(derecha)
        self._crear_panel_gantt(derecha)

    def _crear_panel_cpu(self, padre):
        marco = ttk.LabelFrame(padre, text="CPU", padding=6)
        marco.pack(fill="x", pady=(0, 6))
        self.etiqueta_cpu = tk.Label(
            marco, text="-", font=("Segoe UI", 20, "bold"), width=10,
            relief="ridge", borderwidth=3, bg="#EAF2FB", fg="#1F3A5F")
        self.etiqueta_cpu.pack(pady=(0, 4))
        self.var_tramo = tk.StringVar()
        ttk.Label(marco, textvariable=self.var_tramo, anchor="center").pack(fill="x")
        self.var_cpu_acumulada = tk.StringVar()
        ttk.Label(marco, textvariable=self.var_cpu_acumulada, anchor="center",
                  style="Valor.TLabel").pack(fill="x", pady=(2, 0))

    def _crear_panel_listos(self, padre):
        marco = ttk.LabelFrame(padre, text="PROCESOS LISTOS (tiempo restante)",
                               padding=6)
        marco.pack(fill="x", pady=(0, 6))
        self.tabla_listos = ttk.Treeview(
            marco, columns=COLUMNAS_LISTOS, show="headings", height=5,
            selectmode="none")
        anchos = (70, 75, 75, 70, 90)
        for columna, ancho in zip(COLUMNAS_LISTOS, anchos):
            self.tabla_listos.heading(columna, text=columna)
            self.tabla_listos.column(columna, width=ancho, anchor="center")
        self.tabla_listos.tag_configure("cpu", background="#CDE7FF")
        self.tabla_listos.pack(fill="x")

    def _crear_panel_estado(self, padre):
        marco = ttk.LabelFrame(padre, text="ESTADO DEL SISTEMA", padding=6)
        marco.pack(fill="x")

        self.var_cola = tk.StringVar()
        self.var_nuevos = tk.StringVar()
        self.var_futuros = tk.StringVar()
        self.var_terminados = tk.StringVar()

        # La cola circular solo existe en Round Robin
        if self.simulacion.algoritmo == simulador.ROUND_ROBIN:
            ttk.Label(marco, textvariable=self.var_cola, wraplength=380,
                      justify="left").pack(anchor="w", pady=1)
        for variable in (self.var_nuevos, self.var_futuros, self.var_terminados):
            ttk.Label(marco, textvariable=variable, wraplength=380,
                      justify="left").pack(anchor="w", pady=1)

    def _crear_panel_decision(self, padre):
        marco = ttk.LabelFrame(padre, text="DECISIÓN DEL ALGORITMO", padding=6)
        marco.pack(fill="x", pady=(0, 6))
        self.var_decision = tk.StringVar()
        self.var_motivo = tk.StringVar()
        ttk.Label(marco, textvariable=self.var_decision, style="Valor.TLabel",
                  wraplength=760, justify="left").pack(anchor="w")
        ttk.Label(marco, textvariable=self.var_motivo, wraplength=760,
                  justify="left").pack(anchor="w", pady=(4, 0))

    def _crear_panel_gantt(self, padre):
        marco = ttk.LabelFrame(padre, text="DIAGRAMA DE GANTT (acumulado hasta este paso)",
                               padding=6)
        marco.pack(fill="both", expand=True)
        self.var_gantt_texto = tk.StringVar()
        ttk.Label(marco, textvariable=self.var_gantt_texto, wraplength=760,
                  justify="left").pack(side="bottom", fill="x", pady=(4, 0))
        ids = [p.id for p in self.simulacion.resultado.procesos]
        self.gantt = gantt.GanttInteractivo(marco, ids)

    # ======================================================================
    # Navegación
    # ======================================================================
    def siguiente(self):
        if self.indice < len(self.simulacion.pasos) - 1:
            self.indice += 1
            self._mostrar_paso()

    def anterior(self):
        if self.indice > 0:
            self.indice -= 1
            self._mostrar_paso()

    def reiniciar(self):
        self.indice = 0
        self._mostrar_paso()

    # ======================================================================
    # Mostrar el paso actual
    # ======================================================================
    def _mostrar_paso(self):
        paso = self.simulacion.pasos[self.indice]
        total_pasos = len(self.simulacion.pasos)

        self.var_paso.set(f"Paso {self.indice + 1} de {total_pasos}")
        self.var_tiempo.set(f"Tiempo actual: {paso.tiempo}")
        self.var_evento.set(f"Evento: {paso.evento}")

        self._mostrar_cpu(paso)
        self._mostrar_listos(paso)
        self._mostrar_estado(paso)
        self._mostrar_decision(paso)
        self._mostrar_gantt(paso)
        self._mostrar_resultados(paso)
        self._actualizar_botones()

    def _mostrar_cpu(self, paso):
        if paso.es_final:
            self.etiqueta_cpu.config(text="FIN")
            self.var_tramo.set(f"La simulación terminó en t={paso.tiempo}")
        elif paso.ejecutando is None:
            self.etiqueta_cpu.config(text="INACTIVA")
            self.var_tramo.set(f"Sin proceso desde t={paso.tiempo} hasta t={paso.fin}")
        else:
            self.etiqueta_cpu.config(text=paso.ejecutando)
            self.var_tramo.set(f"Ejecuta desde t={paso.tiempo} hasta t={paso.fin} "
                               f"({paso.fin - paso.tiempo} unidades)")

        # CPU acumulada hasta el final de este paso (la misma parte que muestra el Gantt)
        segmentos = simulador.segmentos_del_paso(self.simulacion, self.indice)
        ocupada = sum(fin - inicio for id_proceso, inicio, fin in segmentos
                      if id_proceso is not None)
        inactiva = sum(fin - inicio for id_proceso, inicio, fin in segmentos
                       if id_proceso is None)
        self.var_cpu_acumulada.set(f"CPU ocupada: {ocupada} | inactiva: {inactiva}")

    def _mostrar_listos(self, paso):
        self._vaciar_tabla(self.tabla_listos)
        for id_proceso, restante, prioridad, llegada in paso.listos:
            en_cpu = (id_proceso == paso.ejecutando)
            self.tabla_listos.insert(
                "", "end",
                values=(id_proceso, restante, prioridad, llegada,
                        "En CPU" if en_cpu else "Esperando"),
                tags=("cpu",) if en_cpu else ())

    def _mostrar_estado(self, paso):
        nuevos = ", ".join(f"{i} (t={t})" for i, t in paso.nuevos) or "ninguna"
        futuros = ", ".join(f"{i} (t={t})" for i, t in paso.futuros) or "ninguno"
        terminados = ", ".join(paso.terminados) or "ninguno"
        cola = " → ".join(paso.cola) if paso.cola else "vacía"
        total = len(self.simulacion.resultado.procesos)

        self.var_cola.set(f"Cola circular (frente → final): {cola}")
        self.var_nuevos.set(f"Llegadas desde el paso anterior: {nuevos}")
        self.var_futuros.set(f"Aún no llegan: {futuros}")
        self.var_terminados.set(
            f"Procesos completados: {len(paso.terminados)} de {total}\n"
            f"Terminados: {terminados}")    
    def _mostrar_decision(self, paso):
        if paso.es_final:
            decision = f"Simulación finalizada en t={paso.tiempo}."
        elif paso.ejecutando is None:
            decision = f"La CPU queda inactiva de t={paso.tiempo} a t={paso.fin}."
        else:
            decision = f"Se ejecuta {paso.ejecutando} de t={paso.tiempo} a t={paso.fin}."
        self.var_decision.set("Decisión: " + decision)
        self.var_motivo.set("Motivo: " + paso.explicacion)

    def _mostrar_gantt(self, paso):
        sim = self.simulacion
        segmentos = simulador.segmentos_del_paso(sim, self.indice)
        instante = None if paso.es_final else paso.tiempo
        self.gantt.actualizar(segmentos, f"Gantt acumulado - {sim.algoritmo}",
                              sim.resultado.tiempo_total, instante)

        partes = [f"{inicio}-{fin} {'Ocioso' if id_proceso is None else id_proceso}"
                  for id_proceso, inicio, fin in segmentos]
        self.var_gantt_texto.set("Gantt: " + " | ".join(partes))

    def _mostrar_resultados(self, paso):
        self._vaciar_tabla(self.tabla_resultados)
        variables = (self.var_prom_espera, self.var_prom_retorno,
                     self.var_prom_respuesta, self.var_tiempo_total,
                     self.var_utilizacion, self.var_cpu, self.var_completados)

        if not paso.es_final:
            for variable in variables:
                variable.set("-")
            return

        resultado = self.simulacion.resultado
        for p in resultado.procesos:
            self.tabla_resultados.insert("", "end", values=(
                p.id, p.llegada, p.ejecucion, p.prioridad, p.inicio,
                p.finalizacion, p.retorno, p.espera, p.respuesta))
        self.var_prom_espera.set(f"{resultado.promedio_espera:.2f}")
        self.var_prom_retorno.set(f"{resultado.promedio_retorno:.2f}")
        self.var_prom_respuesta.set(f"{resultado.promedio_respuesta:.2f}")
        self.var_tiempo_total.set(str(resultado.tiempo_total))
        self.var_utilizacion.set(f"{resultado.utilizacion_cpu:.2f} %")
        self.var_cpu.set(f"{resultado.tiempo_cpu_ocupada} / "
                         f"{resultado.tiempo_cpu_inactiva} unidades")
        self.var_completados.set(f"{resultado.procesos_completados} de "
                                 f"{len(resultado.procesos)}")

    def _actualizar_botones(self):
        ultimo = len(self.simulacion.pasos) - 1
        self.boton_anterior.state(["disabled"] if self.indice == 0 else ["!disabled"])
        self.boton_siguiente.state(["disabled"] if self.indice == ultimo else ["!disabled"])

    @staticmethod
    def _vaciar_tabla(tabla):
        for fila in tabla.get_children():
            tabla.delete(fila)