# Simulador de Planificación de Procesos

## 1. Objetivo

Simular la planificación de procesos de un sistema operativo. El usuario introduce procesos, selecciona una política de planificación y el sistema calcula la ejecución, los tiempos de espera, retorno y respuesta, además de representar visualmente el comportamiento mediante un diagrama de Gantt.

## 2. Tecnologías

- Python 3
- Tkinter + ttk (interfaz gráfica)
- Matplotlib (solo para dibujar el diagrama de Gantt)
- dataclasses (clase `Proceso` y resultado de la simulación)

No se usan frameworks web, bases de datos, APIs ni conexión a Internet.

## 3. Algoritmos

| Algoritmo | Tipo | Criterio de selección |
|---|---|---|
| FCFS / FIFO | No expulsivo | Orden de llegada |
| SJF | No expulsivo | Menor tiempo de ejecución (desempate: llegada, luego ID) |
| Prioridad no expulsiva | No expulsivo | Mayor prioridad: 1 es la más alta (desempate: llegada, luego ID) |
| SRTF | Expulsivo | Menor tiempo restante, revisado en cada unidad de tiempo |
| Prioridad expulsiva | Expulsivo | Si llega un proceso de mayor prioridad, expulsa al actual |
| Round Robin | Expulsivo | Cola circular con quantum configurable (debe ser mayor que 0) |

## 4. Planificación expulsiva y no expulsiva

- **No expulsiva:** cuando un proceso obtiene la CPU, la conserva hasta terminar su ráfaga. Aunque llegue otro proceso más conveniente, debe esperar.
- **Expulsiva:** el sistema puede quitarle la CPU a un proceso en ejecución (por la llegada de otro con mejor criterio o por fin del quantum). El proceso interrumpido vuelve a la cola y reanuda después, por lo que puede aparecer varias veces en el Gantt.

## 5. Estructura

```text
simulador_planificacion/
├── main.py          Punto de entrada
├── proceso.py       Clase Proceso (datos y resultados)
├── algoritmos.py    Los seis algoritmos de planificación
├── simulador.py     Intermediario: ejecuta, calcula promedios y compara
├── interfaz.py      Interfaz gráfica (Tkinter)
├── gantt.py         Diagrama de Gantt (Matplotlib)
├── requirements.txt
└── README.md
```

Formato de los segmentos del Gantt: `(id_proceso, inicio, fin)`. Si la CPU está inactiva, `id_proceso` vale `None`.

## 6. Instalación

```bash
pip install -r requirements.txt
```

Tkinter normalmente viene con Python. En algunas distribuciones de Linux hay que instalarlo aparte:

```bash
sudo apt install python3-tk
```

## 7. Ejecución

```bash
python main.py
```

## 8. Ejemplo de uso

1. Ingresar los procesos (ID, llegada, ejecución, prioridad) y presionar **AGREGAR**:

```text
P1 | Llegada 0 | Ejecución 8 | Prioridad 2
P2 | Llegada 1 | Ejecución 4 | Prioridad 1
P3 | Llegada 2 | Ejecución 2 | Prioridad 3
P4 | Llegada 3 | Ejecución 1 | Prioridad 2
```

2. Elegir un algoritmo (si es Round Robin, indicar el quantum) y presionar **SIMULAR**.
3. Observar la tabla de resultados, los promedios y el diagrama de Gantt.
4. Presionar **COMPARAR ALGORITMOS** para ver los promedios de los seis algoritmos con los mismos procesos.

Resultados esperados con estos datos (para verificar):

```text
FCFS:  P1 0-8 | P2 8-12 | P3 12-14 | P4 14-15
       Espera promedio 7.00 | Retorno promedio 10.75 | Respuesta promedio 7.00

SRTF:  P1 0-1 | P2 1-2 | P3 2-4 | P4 4-5 | P2 5-8 | P1 8-15
       Espera promedio 2.75 | Retorno promedio 6.50 | Respuesta promedio 0.25
```

Lectura del Gantt: las barras rayadas son reanudaciones, el triángulo rojo marca una interrupción y la barra gris punteada indica CPU inactiva.

## 9. Fórmulas utilizadas

```text
Retorno   = Finalización - Llegada
Espera    = Retorno - Ejecución
Respuesta = Primer inicio - Llegada

Utilización de CPU = (tiempo con CPU ocupada / tiempo total) * 100
```

El tiempo total es el instante en que termina el último proceso. Los períodos de CPU inactiva (incluido el tiempo antes de la primera llegada) cuentan dentro del tiempo total.