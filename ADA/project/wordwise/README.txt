WORDWISE - Corrector ortografico y autocompletado (C++17)
Curso: Analisis y Diseno de Algoritmos (SIS214) - Unidad I

ARCHIVOS
  main.cpp                 Menu principal
  utils.hpp                Tipos, normalizacion de texto, carga del diccionario, cronometro
  hash_table.hpp           Tabla hash con encadenamiento (verificar palabra)
  trie.hpp                 Arbol de prefijos (autocompletado)
  heap.hpp                 Heap / cola de prioridad (top-K sugerencias)
  edit_distance.hpp        Distancia de edicion: recursiva vs programacion dinamica
  sorting.hpp              Burbuja, insercion, seleccion, Merge Sort, Quick Sort
  search.hpp               Busqueda lineal y binaria
  corrector.hpp            Sugerencias de correccion (distancia + heap)
  benchmark.hpp            Mediciones de tiempo (EV1)
  diccionario.txt          6 625 palabras en espanol con frecuencia simulada
  generar_diccionario.py   Script que genero el diccionario (opcional)
  resultados_benchmark.*   Resultados de ejemplo (los tiempos cambian segun el equipo)

COMPILAR
  Linux / Mac / Windows con MinGW:
      g++ -O2 -std=c++17 main.cpp -o wordwise
  Visual Studio (Developer Command Prompt):
      cl /O2 /EHsc /std:c++17 main.cpp /Fe:wordwise.exe

EJECUTAR (desde la carpeta donde esta diccionario.txt)
  ./wordwise                          Menu interactivo
  ./wordwise --benchmark              Todos los benchmarks (aprox. 40 s), guarda resultados_benchmark.csv
  ./wordwise --benchmark --completo   Incluye los O(n^2) con n=50 000 y 100 000 (tarda varios minutos)

NOTAS
  - Escriba las palabras sin tildes en la consola (el programa tambien normaliza tildes UTF-8 y la enie).
  - Si compila SIN -O2 los tiempos seran mayores, pero las proporciones entre algoritmos se mantienen.
