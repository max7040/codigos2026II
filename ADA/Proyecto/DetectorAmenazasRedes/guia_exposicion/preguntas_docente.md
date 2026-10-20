# Preguntas probables del docente y respuestas sugeridas

> Responde con tus palabras; estas son ideas base.

**1. ¿Usa inteligencia artificial?** No. Son reglas con umbrales; cada alerta muestra el dato que la justifica.

**2. ¿Por qué un grafo?** Porque una red es un conjunto de entidades y relaciones. Permite consultar vecinos y grados directamente.

**3. ¿Lista o matriz de adyacencia? ¿Cuál usa y por qué?** Uso lista: O(n+m) de espacio y vecinos en O(grado); las redes reales son dispersas. La matriz usa O(n²) pero responde «¿hay arista?» en O(1). La app compara ambas.

**4. ¿Qué hace NetworkX si el grafo es propio?** Solo calcula las posiciones de los nodos para dibujar. El modelo y las reglas son míos, para demostrar la implementación académica.

**5. ¿Por qué Merge Sort para ordenar las alertas?** Es O(n log n) en todos los casos; evita el peor caso O(n²) de Quick Sort.

**6. ¿Cuándo es mejor la búsqueda binaria?** Cuando la lista está ordenada y se busca varias veces: O(log n) frente a O(n). Si hay que ordenar solo para buscar una vez, no compensa.

**7. ¿Cómo maneja la tabla hash las colisiones?** Con encadenamiento: cada casillero guarda una lista de pares. Si el factor de carga pasa de 0,75, duplica la capacidad y reubica las claves.

**8. ¿Por qué limitó Fibonacci recursivo a n ≤ 35?** Su costo es exponencial (≈ 2ⁿ) por subproblemas repetidos y bloquearía la aplicación. Memoización y tabulación lo bajan a O(n).

**9. ¿Diferencia entre voraz y programación dinámica?** El voraz toma la mejor decisión local y no la revisa (óptimo en la mochila fraccionaria). La PD resuelve subproblemas y guarda resultados para combinar (necesaria en la mochila 0/1).

**10. ¿Cómo se calcula el riesgo?** `min(100, round(50 × valor/umbral))`. Es una convención didáctica del proyecto, no un estándar.

**11. ¿Puede dar falsos positivos?** Sí: un servidor central es legítimamente muy conectado. Por eso son umbrales configurables y recomendaciones generales, no veredictos.

**12. ¿Sus tiempos demuestran que Merge Sort es siempre más rápido?** No. Dependen del equipo, el tamaño y la implementación. Mido con `perf_counter`, repito, uso los mismos datos y verifico el resultado, pero son mediciones, no la complejidad teórica.

**13. ¿Cómo garantiza que el código funciona?** Con pruebas pytest: casos normales, listas vacías, repetidos, colisiones, importaciones inválidas y reglas del detector. (Menciona cuántas pasaron **solo si las ejecutaste**.)

**14. ¿Qué pasa con una importación inválida?** Se rechaza sin romper la app y se muestran todos los errores con su posición (nodo n.º, fila del CSV).

**15. ¿Qué mejoraría?** BFS/DFS para caminos y componentes, caminos mínimos, reglas temporales y datos más realistas; son de unidades posteriores.

**16. ¿Por qué Streamlit usa `session_state`?** Porque cada interacción reejecuta el script; sin él, la red se reiniciaría.

**17. ¿Qué es la complejidad espacial de Merge Sort?** O(n) por las listas auxiliares al mezclar.

**18. ¿Qué haría si le piden escanear una red real?** Fuera de alcance: el proyecto es educativo y trabaja solo con datos simulados.
