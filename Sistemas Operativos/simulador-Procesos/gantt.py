from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PALETA = ["#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2",
          "#EECA3B", "#B279A2", "#FF9DA6", "#9D755D", "#BAB0AC"]
COLOR_OCIOSO = "#E0E0E0"
ALTURA_BARRA = 0.6


def _asignar_colores(segmentos, ids_colores=None):
    
    if ids_colores is not None:
        ids = sorted(set(ids_colores))
    else:
        ids = sorted({id_proceso for id_proceso, _, _ in segmentos
                      if id_proceso is not None})
    return {id_proceso: PALETA[i % len(PALETA)] for i, id_proceso in enumerate(ids)}


def _clasificar_segmentos(segmentos):
   
    resultado = []
    for i, (id_proceso, _, _) in enumerate(segmentos):
        if id_proceso is None:
            resultado.append((False, False))
            continue
        ya_ejecuto = any(otro == id_proceso for otro, _, _ in segmentos[:i])
        ejecutara_despues = any(otro == id_proceso for otro, _, _ in segmentos[i + 1:])
        resultado.append((ya_ejecuto, ejecutara_despues))
    return resultado


def _dibujar_segmento(eje, id_proceso, inicio, fin, colores, reanuda, interrumpido):
    ancho = fin - inicio
    centro = inicio + ancho / 2

    # CPU inactiva
    if id_proceso is None:
        eje.barh(0, ancho, left=inicio, height=ALTURA_BARRA, color=COLOR_OCIOSO,
                 edgecolor="gray", linewidth=0.8, hatch="..")
        eje.text(centro, 0, "Ocioso", ha="center", va="center",
                 fontsize=7, color="dimgray")
        return

    # Proceso en ejecución (rayado si es una reanudación)
    eje.barh(0, ancho, left=inicio, height=ALTURA_BARRA, color=colores[id_proceso],
             edgecolor="black", linewidth=0.8, hatch="//" if reanuda else None)
    caja = None
    if reanuda:
        caja = dict(boxstyle="round,pad=0.15", facecolor="white",
                    edgecolor="none", alpha=0.8)
    eje.text(centro, 0, id_proceso, ha="center", va="center",
             fontsize=9, fontweight="bold", bbox=caja)

    # Marca de interrupción al final del segmento
    if interrumpido:
        eje.plot(fin, ALTURA_BARRA / 2 + 0.05, marker="v", color="red",
                 markersize=7, linestyle="None", clip_on=False)


def _configurar_ejes(eje, segmentos, tiempo_maximo=None):
    inicio_total = min(inicio for _, inicio, _ in segmentos)
    fin_total = max(fin for _, _, fin in segmentos)
    if tiempo_maximo is not None:
        # En paso a paso el eje ya muestra el tiempo total desde el inicio
        fin_total = max(fin_total, tiempo_maximo)

    # Marcas del eje X: todos los instantes donde empieza o termina un segmento
    marcas = sorted({t for _, inicio, fin in segmentos for t in (inicio, fin)})

    eje.set_xlim(inicio_total, fin_total)
    eje.set_ylim(-0.6, 0.7)
    eje.set_yticks([])
    eje.set_xticks(marcas)
    rotacion = 90 if len(marcas) > 25 else 0
    eje.tick_params(axis="x", labelsize=8, labelrotation=rotacion)
    eje.set_xlabel("Tiempo (unidades)", fontsize=9)
    for lado in ("top", "right", "left"):
        eje.spines[lado].set_visible(False)


def _agregar_leyenda(eje, con_instante=False):
    elementos = [
        Patch(facecolor="white", edgecolor="black", label="Ejecución"),
        Patch(facecolor="white", edgecolor="black", hatch="//", label="Reanudación"),
        Line2D([0], [0], marker="v", color="red", linestyle="None",
               label="Interrupción"),
        Patch(facecolor=COLOR_OCIOSO, edgecolor="gray", hatch="..",
              label="CPU inactiva"),
    ]
    if con_instante:
        elementos.append(Line2D([0], [0], color="black", linestyle="--",
                                label="Instante actual"))
    eje.legend(handles=elementos, loc="lower center", bbox_to_anchor=(0.5, 1.0),
               ncol=len(elementos), fontsize=8, frameon=False)


def dibujar_en_figura(figura, segmentos, titulo="Diagrama de Gantt",
                      tiempo_maximo=None, tiempo_actual=None, ids_colores=None):
    
    figura.clear()
    eje = figura.add_subplot(111)

    if not segmentos:
        eje.text(0.5, 0.5, "Sin datos para mostrar", ha="center", va="center",
                 transform=eje.transAxes)
        eje.axis("off")
        return

    colores = _asignar_colores(segmentos, ids_colores)
    detalles = _clasificar_segmentos(segmentos)

    for (id_proceso, inicio, fin), (reanuda, interrumpido) in zip(segmentos, detalles):
        _dibujar_segmento(eje, id_proceso, inicio, fin, colores, reanuda, interrumpido)

    _configurar_ejes(eje, segmentos, tiempo_maximo)

    if tiempo_actual is not None:
        eje.axvline(tiempo_actual, color="black", linestyle="--", linewidth=1)

    _agregar_leyenda(eje, con_instante=tiempo_actual is not None)
    figura.text(0.5, 0.97, titulo, ha="center", va="top",
                fontsize=10, fontweight="bold")
    figura.tight_layout(rect=(0, 0, 1, 0.9))


def crear_figura(segmentos, titulo="Diagrama de Gantt"):
    """Construye la figura de Matplotlib a partir de los segmentos."""
    figura = Figure(figsize=(7.5, 3.0), dpi=100)
    dibujar_en_figura(figura, segmentos, titulo)
    return figura


def insertar_en_tkinter(figura, contenedor):
   
    canvas = FigureCanvasTkAgg(figura, master=contenedor)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.pack(fill="both", expand=True)
    return widget


class GanttInteractivo:
    

    def __init__(self, contenedor, ids_procesos):
        self.ids_procesos = list(ids_procesos)
        self.figura = Figure(figsize=(7.5, 3.2), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figura, master=contenedor)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def actualizar(self, segmentos, titulo, tiempo_maximo, tiempo_actual):
        dibujar_en_figura(self.figura, segmentos, titulo,
                          tiempo_maximo=tiempo_maximo,
                          tiempo_actual=tiempo_actual,
                          ids_colores=self.ids_procesos)
        self.canvas.draw()