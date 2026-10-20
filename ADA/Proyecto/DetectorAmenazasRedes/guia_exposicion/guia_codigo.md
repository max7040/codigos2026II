# Guía del código

Orden recomendado de lectura: `estructuras/grafo.py` → `analisis/detector.py` → `visualizacion/grafo_visual.py` → `interfaz/` → `algoritmos/`.

## Raíz
- `app.py`: configura la página, crea el menú lateral (`st.radio`) y llama a `mostrar()` de la página elegida.
- `requirements.txt`: versiones compatibles de streamlit, networkx, plotly, pytest y numpy.
- `pytest.ini`: indica que las pruebas están en `pruebas/` y que el proyecto es la raíz de importación.
- `data/ejemplo_red.json`: red de ejemplo (12 nodos, 18 conexiones, dirigida).

## `estructuras/`
- **`grafo.py` → `Grafo`:** `agregar_nodo`, `editar_nodo`, `eliminar_nodo`, `agregar_conexion`, `editar_conexion`, `eliminar_conexion`, `existe_conexion`, `vecinos`, `predecesores`, `grado`, `grado_entrada`, `grado_salida`, `lista_adyacencia`, `matriz_adyacencia`, `a_dict`, `copiar`. Lanza `ErrorGrafo` con mensajes claros. Valida: sin lazos, sin duplicados, peso > 0, frecuencia y eventos ≥ 0.
- **`tabla_hash.py` → `TablaHash`:** lista de casilleros; cada casillero es una lista de pares (encadenamiento). `_hash` calcula un número para la clave y `% capacidad` da el casillero. Si el factor de carga supera 0,75 se duplica la capacidad (`_redimensionar`).
- **`arbol_binario.py` → `ArbolBinarioBusqueda`:** inserción, búsqueda y eliminación iterativas; `inorden` devuelve las claves ordenadas; `altura`, `minimo`, `maximo`.

## `algoritmos/`
- `ordenamiento.py`: `burbuja`, `insercion`, `seleccion` (devuelven una lista nueva).
- `divide_conquista.py`: `merge_sort` (divide, ordena, `_mezclar`) y `quick_sort` (pivote por mediana de tres, `_particionar`).
- `busqueda.py`: `busqueda_lineal`, `busqueda_binaria`, `busqueda_binaria_recursiva` (devuelven índice o −1).
- `recursion.py`: factorial y cuatro Fibonacci (`fibonacci_recursivo` limitado a n ≤ 35).
- `voraces.py`: `mochila_fraccionaria`, `seleccion_actividades`.
- `programacion_dinamica.py`: `mochila_01` (tabla n×W y reconstrucción) y `cadena_matrices` (costos y paréntesis óptimos).

## `analisis/`
- **`detector.py`:** `ConfigDetector` (umbrales), `REGLAS` (nombre y recomendación), funciones `regla_*` (solo devuelven hallazgos), `calcular_riesgo`, `detectar` (aplica reglas, calcula riesgo, ordena con Merge Sort y crea objetos `Alerta`), `resumen_por_nivel`.
- **`metricas_grafo.py`:** `nodos_por_grado`, `comparar_representaciones`, `crecimiento_representaciones`.
- **`benchmark.py`:** `generar_datos` (semilla fija), `medir` (copias + `perf_counter` + verificación), `ejecutar_benchmark`.

## `utils/validaciones.py`
`importar_json`, `exportar_json`, `importar_csv`, `exportar_csv`. Acumulan **todos** los errores y los devuelven juntos en `ErrorValidacion.errores`.

## `visualizacion/`
- `grafo_visual.py`: `a_networkx` (convierte), `calcular_posiciones` (layouts), `construir_figura` (trazos por tipo de nodo, aristas normales y en alerta, flechas si es dirigido, pesos y leyenda).
- `estadisticas.py`: una función por gráfico; solo presentan datos ya calculados.

## `interfaz/`
`estado.py` (`st.session_state`: grafo, config, benchmark) y `pagina_*.py` (una por sección; cada una expone `mostrar()`).

## Cómo seguir el flujo de una acción
*Agregar una conexión:* `pagina_constructor` → formulario → `grafo.agregar_conexion()` (valida) → `st.session_state.grafo` conserva el cambio → al abrir *Detector*, `detectar()` recalcula las alertas con la red actual.

## Para probar en la terminal
```powershell
pytest                       # todas las pruebas
pytest pruebas/test_grafo.py # una sola
```
