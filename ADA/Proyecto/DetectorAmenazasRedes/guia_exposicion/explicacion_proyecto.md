# Explicación del proyecto — Detector de Amenazas en Redes

> Esta guía es para que **entiendas** el proyecto y lo expliques con tus palabras. No es un discurso para memorizar.

## 1. El problema y la solución
**Problema:** una red tiene equipos, servidores y cuentas que se comunican. Queremos representarla y marcar comportamientos inusuales (por ejemplo, un servidor con demasiadas conexiones) con criterios que se puedan justificar.

**Solución:** modelar la red como un **grafo** (nodos = equipos/servidores/cuentas; aristas = conexiones con peso, frecuencia y eventos), aplicar **reglas con umbrales** y mostrar cada alerta con la regla activada, los datos que la justifican, un riesgo y una recomendación.

**Qué NO es:** no escanea redes reales, no ataca nada y **no usa inteligencia artificial**. Las alertas son ejemplos educativos, no pruebas de una amenaza.

## 2. Arquitectura (capas)
```
Datos (Grafo) → Reglas (detector) → Cálculo de riesgo → Presentación (Streamlit + Plotly)
```
| Carpeta | Para qué sirve |
|---|---|
| `algoritmos/` | Ordenamiento, búsqueda, recursión, divide y vencerás, voraces, programación dinámica (hechos a mano) |
| `estructuras/` | Tabla hash, árbol binario de búsqueda, grafo |
| `analisis/` | Detector de reglas, métricas del grafo, benchmark |
| `visualizacion/` | Dibujo del grafo y gráficos estadísticos |
| `utils/` | Validar e importar/exportar JSON y CSV |
| `interfaz/` | Una página de Streamlit por sección |
| `pruebas/` | Pruebas con pytest |
| `app.py` | Punto de entrada: menú lateral |

## 3. Cómo funciona el grafo
Cada nodo tiene `id` y `tipo`. La estructura interna es una **lista de adyacencia** con diccionarios: `_ady[u][v] = propiedades de u→v`. Ventajas: consultar vecinos de un nodo cuesta O(grado) y el espacio es O(n+m). La **matriz de adyacencia** se genera aparte (n×n) para compararlas: ocupa O(n²) pero responde «¿existe la arista u–v?» en O(1).

## 4. Streamlit, NetworkX y Plotly (las tres bibliotecas)
- **Streamlit:** convierte un script de Python en una página web. Cada vez que el usuario toca un control, el script **se vuelve a ejecutar de arriba abajo**. Por eso la red se guarda en `st.session_state`: es la «memoria» que sobrevive entre ejecuciones.
- **NetworkX:** biblioteca de grafos. Aquí solo la usamos para **calcular posiciones (x, y)** de los nodos (distribuciones resorte, circular, concéntrica, aleatoria). Nuestro modelo de datos y las reglas son propios.
- **Plotly:** dibuja gráficos interactivos. Recibe las posiciones y dibuja puntos (nodos), líneas (aristas) y textos emergentes al pasar el cursor.

**Cómo se conectan:** `Grafo` (propio) → `a_networkx()` → `nx.spring_layout` etc. → posiciones → `construir_figura()` con Plotly → `st.plotly_chart()`.

## 5. El detector y el riesgo
Cuatro reglas (umbrales por defecto entre paréntesis):
1. `GRADO_ALTO`: nodo con ≥ 5 conexiones.
2. `FRECUENCIA_ALTA`: conexión con frecuencia ≥ 100.
3. `EVENTOS_REPETIDOS`: conexión con ≥ 50 eventos.
4. `CUENTA_MULTI_SERVIDOR`: cuenta conectada a ≥ 3 servidores.

**Riesgo:** `puntaje = min(100, round(50 × valor / umbral))`. Si valor = umbral → 50 (Bajo). Si valor ≥ 2×umbral → 100 (Crítico). Niveles: Bajo [50,60), Medio [60,80), Alto [80,100), Crítico = 100.

**Ejemplo:** `pc-03 → srv-web` tiene 300 eventos y el umbral es 50 → 50×300/50 = 300 → tope 100 → **Crítico**.

## 6. Dónde se aplica cada algoritmo
| Algoritmo / estructura | Dónde se usa |
|---|---|
| Merge Sort | Ordenar alertas por riesgo y nodos por grado |
| Burbuja, inserción, selección, Quick Sort | Laboratorio y benchmark |
| Búsqueda lineal / binaria | Laboratorio |
| Tabla hash | Laboratorio (colisiones y factor de carga) |
| Árbol binario de búsqueda | Laboratorio (inorden, altura) |
| Factorial / Fibonacci | Laboratorio: recursivo vs iterativo vs memoización vs tabulación |
| Voraces, programación dinámica | Laboratorio |
| Lista y matriz de adyacencia | Modelo del grafo y comparación de crecimiento |

## 7. Complejidades (resumen)
Burbuja/Inserción/Selección O(n²) · Merge Sort O(n log n) (espacio O(n)) · Quick Sort O(n log n) promedio, O(n²) peor · Lineal O(n) · Binaria O(log n) · Tabla hash O(1) promedio · BST O(h) · Fibonacci recursivo ≈ O(2ⁿ), con memoización/tabulación O(n) · Mochila 0/1 O(nW) · Cadena de matrices O(n³).

## 8. Gráficos y experimentos
- *Nodos por grado*: barras largas = nodos muy conectados.
- *Eventos por conexión*: las más altas activan la regla de repetición.
- *Alertas por nivel*: cuántas alertas hay de cada riesgo.
- *Representaciones*: valores **calculados con fórmulas** (no mediciones de memoria).
- *Benchmark*: tiempo promedio vs n, con `time.perf_counter()`, mismos datos para todos y resultado verificado. **Los tiempos dependen de tu equipo**; no son la complejidad teórica.

## 9. Limitaciones y mejoras posibles
Umbrales fijos, solo estructura (no contenido del tráfico), posibles falsos positivos, datos simulados. Ampliaciones (no obligatorias de la unidad): BFS/DFS, caminos mínimos, detección de componentes.

## 10. Guion oral (~10 minutos)
1. **(1 min) Problema:** «Quise modelar una red como grafo y marcar conexiones sospechosas de forma explicable.»
2. **(1 min) Alcance:** simulado, sin IA, educativo.
3. **(2 min) Modelo y estructuras:** grafo con lista de adyacencia; matriz para comparar; tabla hash y BST.
4. **(2 min) Algoritmos:** qué implementé a mano y su complejidad; mostrar el Laboratorio.
5. **(2 min) Detector:** 4 reglas, fórmula de riesgo, abrir una alerta y leer su justificación.
6. **(1 min) Visualización:** NetworkX calcula posiciones, Plotly dibuja.
7. **(1 min) Experimentos y pruebas:** benchmark y pytest; aclarar que los tiempos dependen del equipo.
8. **(Cierre)** Limitaciones y mejoras.

## 11. Demostración práctica (paso a paso)
1. `.\.venv\Scripts\Activate.ps1` y `streamlit run app.py`.
2. **Inicio:** mostrar indicadores y distribución de riesgo.
3. **Visualización:** cambiar la distribución, pasar el cursor sobre `srv-web`.
4. **Detector:** abrir la alerta `A001` y leer regla, datos y recomendación; bajar un umbral y ver cómo aparecen más alertas.
5. **Constructor:** agregar un nodo y una conexión con 500 eventos; volver al Detector y ver la nueva alerta.
6. **Laboratorio:** ordenar una lista, buscar un valor, mostrar Fibonacci recursivo vs memoización.
7. **Estadísticas:** ejecutar el benchmark (100, 500, 1000) y comentar el resultado **que salga en tu equipo**.
