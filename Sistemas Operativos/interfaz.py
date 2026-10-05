import tkinter as tk
from tkinter import messagebox, ttk

import gantt
import simulador
from proceso import Proceso

COLUMNAS_PROCESOS = ("ID", "Llegada", "Ejecución", "Prioridad")
COLUMNAS_RESULTADOS = ("ID", "Llegada", "Ejecución", "Prioridad", "Inicio",
                       "Finalización", "Retorno", "Espera", "Respuesta")
COLUMNAS_COMPARACION = ("Algoritmo", "Espera promedio", "Retorno promedio",
                        "Respuesta promedio")


class InterfazSimulador:
    def __init__(self, raiz):
        self.raiz = raiz
        self.procesos = []          # lista de objetos Proceso ingresados
        self.contenido_gantt = None  # widget actual dentro del panel del Gantt

        raiz.title("Simulador de Planificación de Procesos")
        raiz.geometry("1280x820")
        raiz.minsize(1150, 720)

        self._configurar_estilos()
        self._crear_encabezado()

        cuerpo = ttk.Frame(raiz, padding=10)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        izquierda = ttk.Frame(cuerpo)
        izquierda.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        derecha = ttk.Frame(cuerpo)
        derecha.grid(row=0, column=1, sticky="nsew")

        self._crear_panel_entrada(izquierda)
        self._crear_panel_procesos(izquierda)
        self._crear_panel_algoritmo(izquierda)
        self._crear_panel_comparacion(izquierda)
        self._crear_panel_resultados(derecha)
        self._crear_panel_gantt(derecha)

    # ======================================================================
    # Construcción de la interfaz
    # ======================================================================
    def _configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 16, "bold"),
                         foreground="#1F3A5F")
        estilo.configure("Tipo.TLabel", font=("Segoe UI", 10, "bold"),
                         foreground="#1F3A5F")
        estilo.configure("Valor.TLabel", font=("Segoe UI", 10, "bold"))
        estilo.configure("Accion.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        estilo.configure("Treeview", rowheight=22)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _crear_encabezado(self):
        ttk.Label(self.raiz, text="SIMULADOR DE PLANIFICACIÓN DE PROCESOS",
                  style="Titulo.TLabel", anchor="center").pack(fill="x", pady=(10, 4))
        ttk.Separator(self.raiz, orient="horizontal").pack(fill="x", padx=10)

    def _crear_tabla(self, padre, columnas, anchos, alto):
        """Crea un Treeview con barra de desplazamiento y lo devuelve."""
        contenedor = ttk.Frame(padre)
        contenedor.pack(fill="both", expand=True)
        tabla = ttk.Treeview(contenedor, columns=columnas, show="headings",
                             height=alto, selectmode="browse")
        for columna, ancho in zip(columnas, anchos):
            tabla.heading(columna, text=columna)
            tabla.column(columna, width=ancho, anchor="center")
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return tabla

    def _crear_panel_entrada(self, padre):
        marco = ttk.LabelFrame(padre, text="INGRESAR PROCESO", padding=10)
        marco.pack(fill="x", pady=(0, 8))

        self.var_id = tk.StringVar()
        self.var_llegada = tk.StringVar()
        self.var_ejecucion = tk.StringVar()
        self.var_prioridad = tk.StringVar()

        ttk.Label(marco, text="ID:").grid(row=0, column=0, sticky="e", padx=4, pady=3)
        self.entrada_id = ttk.Entry(marco, textvariable=self.var_id, width=10)
        self.entrada_id.grid(row=0, column=1, padx=4, pady=3)

        ttk.Label(marco, text="Llegada:").grid(row=0, column=2, sticky="e", padx=4)
        ttk.Entry(marco, textvariable=self.var_llegada, width=10).grid(
            row=0, column=3, padx=4)

        ttk.Label(marco, text="Ejecución:").grid(row=1, column=0, sticky="e", padx=4, pady=3)
        ttk.Entry(marco, textvariable=self.var_ejecucion, width=10).grid(
            row=1, column=1, padx=4, pady=3)

        ttk.Label(marco, text="Prioridad:").grid(row=1, column=2, sticky="e", padx=4)
        ttk.Entry(marco, textvariable=self.var_prioridad, width=10).grid(
            row=1, column=3, padx=4)

        botones = ttk.Frame(marco)
        botones.grid(row=2, column=0, columnspan=4, pady=(8, 0))
        ttk.Button(botones, text="AGREGAR", command=self.agregar_proceso).pack(
            side="left", padx=4)
        ttk.Button(botones, text="ELIMINAR", command=self.eliminar_proceso).pack(
            side="left", padx=4)
        ttk.Button(botones, text="LIMPIAR", command=self.limpiar_procesos).pack(
            side="left", padx=4)

    def _crear_panel_procesos(self, padre):
        marco = ttk.LabelFrame(padre, text="PROCESOS", padding=8)
        marco.pack(fill="x", pady=(0, 8))
        self.tabla_procesos = self._crear_tabla(
            marco, COLUMNAS_PROCESOS, (85, 85, 85, 85), alto=5)

    def _crear_panel_algoritmo(self, padre):
        marco = ttk.LabelFrame(padre, text="ALGORITMO", padding=10)
        marco.pack(fill="x", pady=(0, 8))

        self.var_algoritmo = tk.StringVar(value="FCFS")
        self.var_quantum = tk.StringVar(value="2")
        self.var_tipo = tk.StringVar()

        ttk.Label(marco, text="Algoritmo:").grid(row=0, column=0, sticky="e", padx=4)
        combo = ttk.Combobox(marco, textvariable=self.var_algoritmo, state="readonly",
                             values=list(simulador.ALGORITMOS.keys()), width=24)
        combo.grid(row=0, column=1, columnspan=2, sticky="w", padx=4, pady=3)
        combo.bind("<<ComboboxSelected>>", self._actualizar_tipo)

        ttk.Label(marco, textvariable=self.var_tipo, style="Tipo.TLabel").grid(
            row=1, column=1, columnspan=2, sticky="w", padx=4)

        ttk.Label(marco, text="Quantum:").grid(row=2, column=0, sticky="e", padx=4, pady=3)
        ttk.Entry(marco, textvariable=self.var_quantum, width=6).grid(
            row=2, column=1, sticky="w", padx=4, pady=3)
        ttk.Label(marco, text="(Round Robin y comparación)").grid(
            row=2, column=2, sticky="w")

        botones = ttk.Frame(marco)
        botones.grid(row=3, column=0, columnspan=3, pady=(8, 4))
        ttk.Button(botones, text="SIMULAR", style="Accion.TButton",
                   command=self.ejecutar_simulacion).pack(side="left", padx=4)
        ttk.Button(botones, text="COMPARAR ALGORITMOS", style="Accion.TButton",
                   command=self.comparar_algoritmos).pack(side="left", padx=4)

        ttk.Label(marco, justify="left", text=(
            "No expulsivos: FCFS, SJF, Prioridad no expulsiva\n"
            "Expulsivos: SRTF, Prioridad expulsiva, Round Robin")).grid(
            row=4, column=0, columnspan=3, sticky="w", padx=4, pady=(4, 0))

        self._actualizar_tipo()

    def _crear_panel_comparacion(self, padre):
        marco = ttk.LabelFrame(padre, text="COMPARACIÓN DE ALGORITMOS", padding=8)
        marco.pack(fill="x")
        self.tabla_comparacion = self._crear_tabla(
            marco, COLUMNAS_COMPARACION, (150, 95, 95, 105), alto=6)
        self.tabla_comparacion.column("Algoritmo", anchor="w")

    def _crear_panel_resultados(self, padre):
        marco = ttk.LabelFrame(padre, text="RESULTADOS", padding=8)
        marco.pack(fill="x", pady=(0, 8))
        self.tabla_resultados = self._crear_tabla(
            marco, COLUMNAS_RESULTADOS, (70, 70, 80, 75, 65, 90, 70, 65, 80), alto=6)

        self.var_prom_espera = tk.StringVar(value="-")
        self.var_prom_retorno = tk.StringVar(value="-")
        self.var_prom_respuesta = tk.StringVar(value="-")
        self.var_tiempo_total = tk.StringVar(value="-")
        self.var_utilizacion = tk.StringVar(value="-")
        self.var_orden = tk.StringVar(value="-")

        estadisticas = [
            ("Promedio de espera:", self.var_prom_espera),
            ("Promedio de retorno:", self.var_prom_retorno),
            ("Promedio de respuesta:", self.var_prom_respuesta),
            ("Tiempo total:", self.var_tiempo_total),
            ("Utilización de CPU:", self.var_utilizacion),
        ]
        cuadro = ttk.Frame(marco)
        cuadro.pack(fill="x", pady=(8, 0))
        for i, (texto, variable) in enumerate(estadisticas):
            fila = i % 3
            columna = (i // 3) * 2
            ttk.Label(cuadro, text=texto).grid(row=fila, column=columna,
                                               sticky="w", padx=(0, 4), pady=1)
            ttk.Label(cuadro, textvariable=variable, style="Valor.TLabel").grid(
                row=fila, column=columna + 1, sticky="w", padx=(0, 30), pady=1)

        ttk.Label(cuadro, text="Orden de ejecución:").grid(
            row=3, column=0, sticky="nw", pady=(4, 0))
        ttk.Label(cuadro, textvariable=self.var_orden, style="Valor.TLabel",
                  wraplength=520, justify="left").grid(
            row=3, column=1, columnspan=3, sticky="w", pady=(4, 0))

    def _crear_panel_gantt(self, padre):
        self.marco_gantt = ttk.LabelFrame(padre, text="DIAGRAMA DE GANTT", padding=8)
        self.marco_gantt.pack(fill="both", expand=True)
        self._mostrar_marcador_gantt()

    # ======================================================================
    # Validaciones
    # ======================================================================
    def _leer_entero(self, texto, nombre):
        texto = texto.strip()
        if texto == "":
            raise ValueError(f"{nombre} no puede estar vacío.")
        try:
            return int(texto)
        except ValueError:
            raise ValueError(f"{nombre} debe ser un número entero.")

    def _leer_proceso_formulario(self):
        """Lee y valida el formulario. Devuelve un Proceso o lanza ValueError."""
        id_texto = self.var_id.get().strip()
        if id_texto == "":
            raise ValueError("El ID no puede estar vacío.")
        if any(p.id.lower() == id_texto.lower() for p in self.procesos):
            raise ValueError(f"El ID '{id_texto}' ya existe. Use un ID distinto.")

        llegada = self._leer_entero(self.var_llegada.get(), "El tiempo de llegada")
        if llegada < 0:
            raise ValueError("El tiempo de llegada no puede ser negativo.")

        ejecucion = self._leer_entero(self.var_ejecucion.get(), "El tiempo de ejecución")
        if ejecucion <= 0:
            raise ValueError("El tiempo de ejecución debe ser mayor que 0.")

        prioridad = self._leer_entero(self.var_prioridad.get(), "La prioridad")
        if prioridad <= 0:
            raise ValueError("La prioridad debe ser mayor que 0.")

        return Proceso(id_texto, llegada, ejecucion, prioridad)

    def _leer_quantum(self):
        texto = self.var_quantum.get().strip()
        try:
            quantum = int(texto)
        except ValueError:
            raise ValueError("El quantum debe ser un número entero mayor que 0.")
        if quantum <= 0:
            raise ValueError("El quantum debe ser mayor que 0.")
        return quantum

    def _validar_hay_procesos(self):
        if not self.procesos:
            raise ValueError("Agregue al menos un proceso antes de simular.")

    # ======================================================================
    # Acciones de los botones
    # ======================================================================
    def agregar_proceso(self):
        try:
            proceso = self._leer_proceso_formulario()
        except ValueError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return

        self.procesos.append(proceso)
        self.tabla_procesos.insert("", "end", values=(
            proceso.id, proceso.llegada, proceso.ejecucion, proceso.prioridad))

        for variable in (self.var_id, self.var_llegada,
                         self.var_ejecucion, self.var_prioridad):
            variable.set("")
        self.entrada_id.focus_set()
        self._limpiar_resultados()

    def eliminar_proceso(self):
        seleccion = self.tabla_procesos.selection()
        if not seleccion:
            messagebox.showwarning("Eliminar proceso",
                                   "Seleccione un proceso de la tabla para eliminarlo.")
            return
        posicion = self.tabla_procesos.index(seleccion[0])
        del self.procesos[posicion]
        self.tabla_procesos.delete(seleccion[0])
        self._limpiar_resultados()

    def limpiar_procesos(self):
        self.procesos.clear()
        self._vaciar_tabla(self.tabla_procesos)
        self._limpiar_resultados()

    def ejecutar_simulacion(self):
        try:
            self._validar_hay_procesos()
            nombre = self.var_algoritmo.get()
            quantum = self._leer_quantum() if nombre == simulador.ROUND_ROBIN else None
            resultado = simulador.simular(self.procesos, nombre, quantum)
        except ValueError as error:
            messagebox.showerror("No se puede simular", str(error))
            return

        self._mostrar_resultados(resultado)

        titulo = f"Diagrama de Gantt - {nombre}"
        if quantum is not None:
            titulo += f" (quantum = {quantum})"
        self._mostrar_gantt(resultado.segmentos, titulo)

    def comparar_algoritmos(self):
        try:
            self._validar_hay_procesos()
            quantum = self._leer_quantum()
            filas = simulador.comparar_algoritmos(self.procesos, quantum)
        except ValueError as error:
            messagebox.showerror("No se puede comparar", str(error))
            return

        self._vaciar_tabla(self.tabla_comparacion)
        for nombre, espera, retorno, respuesta in filas:
            self.tabla_comparacion.insert("", "end", values=(
                nombre, f"{espera:.2f}", f"{retorno:.2f}", f"{respuesta:.2f}"))

    # ======================================================================
    # Mostrar resultados
    # ======================================================================
    def _actualizar_tipo(self, evento=None):
        tipo = simulador.TIPOS[self.var_algoritmo.get()]
        self.var_tipo.set(f"Tipo: {tipo.upper()}")

    def _mostrar_resultados(self, resultado):
        self._vaciar_tabla(self.tabla_resultados)
        for p in resultado.procesos:
            self.tabla_resultados.insert("", "end", values=(
                p.id, p.llegada, p.ejecucion, p.prioridad, p.inicio,
                p.finalizacion, p.retorno, p.espera, p.respuesta))

        self.var_prom_espera.set(f"{resultado.promedio_espera:.2f}")
        self.var_prom_retorno.set(f"{resultado.promedio_retorno:.2f}")
        self.var_prom_respuesta.set(f"{resultado.promedio_respuesta:.2f}")
        self.var_tiempo_total.set(str(resultado.tiempo_total))
        self.var_utilizacion.set(f"{resultado.utilizacion_cpu:.2f} %")

        pasos = ["Ocioso" if x is None else x for x in resultado.orden]
        self.var_orden.set(" → ".join(pasos))

    def _mostrar_gantt(self, segmentos, titulo):
        self._quitar_contenido_gantt()
        figura = gantt.crear_figura(segmentos, titulo)
        self.contenido_gantt = gantt.insertar_en_tkinter(figura, self.marco_gantt)

    def _mostrar_marcador_gantt(self):
        self._quitar_contenido_gantt()
        self.contenido_gantt = ttk.Label(
            self.marco_gantt, text="Presione SIMULAR para ver el diagrama de Gantt.",
            anchor="center")
        self.contenido_gantt.pack(fill="both", expand=True)

    def _quitar_contenido_gantt(self):
        if self.contenido_gantt is not None:
            self.contenido_gantt.destroy()
            self.contenido_gantt = None

    # ======================================================================
    # Utilidades
    # ======================================================================
    def _vaciar_tabla(self, tabla):
        for fila in tabla.get_children():
            tabla.delete(fila)

    def _limpiar_resultados(self):
        """Borra resultados anteriores (quedan desactualizados al cambiar los procesos)."""
        self._vaciar_tabla(self.tabla_resultados)
        self._vaciar_tabla(self.tabla_comparacion)
        for variable in (self.var_prom_espera, self.var_prom_retorno,
                         self.var_prom_respuesta, self.var_tiempo_total,
                         self.var_utilizacion, self.var_orden):
            variable.set("-")
        self._mostrar_marcador_gantt()