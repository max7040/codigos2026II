/*
 * algoritmos_ordenamiento.c
 * ---------------------------------------------------------------------------
 * Programa en C11 que implementa y compara cuatro algoritmos de ordenamiento
 * sobre arreglos de números enteros:
 *
 *   1. Bubble Sort    (burbuja, con detención anticipada)
 *   2. Selection Sort (selección)
 *   3. Insertion Sort (inserción)
 *   4. Merge Sort     (mezcla, divide y vencerás)
 *
 * Características:
 *   - Menú interactivo; cada algoritmo es una función independiente.
 *   - Orden ascendente o descendente (se decide con una sola función de
 *     comparación compartida, por lo que los cuatro métodos se comportan igual).
 *   - Entrada manual validada (máx. MAX_MANUAL elementos) o generación de datos
 *     (aleatorios, ordenados, inversos, casi ordenados) hasta MAX_ELEMENTOS.
 *   - Se conserva una copia del arreglo original: cada algoritmo trabaja sobre
 *     una copia idéntica de los mismos datos.
 *   - Contadores de comparaciones, intercambios y movimientos, y tiempo con
 *     clock() (la impresión NO forma parte del tiempo medido).
 *   - Cada resultado se verifica contra qsort() (solo como referencia de
 *     verificación; qsort no participa en la comparación de algoritmos).
 *
 * Compilación:
 *   gcc -std=c11 -Wall -Wextra -pedantic algoritmos_ordenamiento.c \
 *       -o algoritmos_ordenamiento
 *
 * Nota: los textos que se imprimen en consola usan solo caracteres ASCII para
 * que se vean bien en cualquier terminal (incluida la de Windows).
 *
 * DEFINICIÓN DE LAS MÉTRICAS (no son idénticas en todos los métodos):
 *   - Comparación : cada evaluación de la relación de orden entre DOS elementos
 *                   del arreglo (no se cuentan las comparaciones de índices de
 *                   los bucles).
 *   - Intercambio : permuta de dos posiciones del arreglo. Solo lo usan Bubble
 *                   y Selection. Cada intercambio equivale a 2 movimientos.
 *   - Movimiento  : escritura de un elemento en una posición del arreglo o del
 *                   arreglo auxiliar. Es la unidad común a los cuatro métodos.
 *                   Insertion cuenta los desplazamientos y la colocación final
 *                   de la clave; Merge cuenta la copia al auxiliar y el regreso
 *                   al arreglo original.
 */

#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* ------------------------------ Constantes ------------------------------- */

#define MAX_MANUAL          1000    /* máximo de elementos en entrada manual   */
#define MAX_ELEMENTOS       100000  /* máximo de elementos generados           */
#define MAX_IMPRESION       40      /* si n <= este valor se imprime completo  */
#define EXTREMOS_IMPRESION  10      /* elementos mostrados al inicio y al fin  */
#define TAM_BUFFER_LINEA    16384   /* tamaño del buffer de lectura de líneas  */
#define ALEATORIO_MIN       (-10000)
#define ALEATORIO_MAX       10000
#define NUM_ALGORITMOS      4
#define TAM_MIN_TIEMPO      2000    /* bajo este n, el tiempo no es fiable     */
#define TAM_AVISO_LENTO     30000   /* sobre este n, los cuadráticos tardan    */

/* -------------------------------- Tipos ---------------------------------- */

typedef enum { ASCENDENTE = 0, DESCENDENTE = 1 } Orden;

typedef enum {
    PATRON_ALEATORIO = 1,
    PATRON_ORDENADO,
    PATRON_INVERSO,
    PATRON_CASI_ORDENADO
} Patron;

/* Contadores de operaciones de un algoritmo. */
typedef struct {
    unsigned long long comparaciones;
    unsigned long long intercambios;
    unsigned long long movimientos;
} Metricas;

/* Arreglo dinámico de enteros con su tamaño. */
typedef struct {
    int *datos;
    int n;
} Arreglo;

/* Firma común de los algoritmos: devuelve 0 si todo salió bien, -1 si falló
 * la reserva de memoria (solo Merge Sort necesita memoria auxiliar). */
typedef int (*FuncionOrdenamiento)(int *, int, Orden, Metricas *);

typedef struct {
    const char *nombre;
    FuncionOrdenamiento ordenar;
    int usa_intercambios;  /* 1 si el método se describe con intercambios */
} Algoritmo;

/* Resultado de ejecutar un algoritmo sobre una copia de los datos. */
typedef struct {
    Metricas metricas;
    double tiempo_ms;
    int estado;        /* 0 = correcto, -1 = error de memoria          */
    int verificacion;  /* 1 = correcto, 0 = incorrecto, -1 = no hecho  */
} Resultado;

/* ============================================================================
 *  NÚCLEO: comparación e intercambio con contadores
 * ========================================================================== */

/*
 * Devuelve 1 si 'a' debe colocarse DESPUÉS de 'b' según el orden elegido,
 * es decir, si el par (a, b) está en orden incorrecto. La relación es
 * ESTRICTA: con elementos iguales devuelve 0. Eso hace que Bubble, Insertion
 * y Merge sean estables. Cada llamada cuenta como una comparación.
 */
static int fuera_de_orden(int a, int b, Orden orden, Metricas *m)
{
    m->comparaciones++;
    return (orden == ASCENDENTE) ? (a > b) : (a < b);
}

/* Intercambia dos posiciones. Cuenta 1 intercambio y 2 movimientos. */
static void intercambiar(int *x, int *y, Metricas *m)
{
    int temporal = *x;
    *x = *y;
    *y = temporal;
    m->intercambios++;
    m->movimientos += 2;
}

/* ============================================================================
 *  ALGORITMOS DE ORDENAMIENTO
 * ========================================================================== */

/*
 * BUBBLE SORT optimizado.
 * En cada pasada se comparan pares adyacentes y se intercambian si están en
 * orden incorrecto; así el mayor (o menor) elemento "sube" al final de la zona
 * no ordenada. Si una pasada completa no realiza ningún intercambio, el arreglo
 * ya está ordenado y se detiene el algoritmo (mejor caso: n-1 comparaciones).
 */
static int ordenar_burbuja(int *a, int n, Orden orden, Metricas *m)
{
    for (int pasada = 0; pasada < n - 1; pasada++) {
        int hubo_intercambio = 0;

        /* Los últimos 'pasada' elementos ya están en su posición final. */
        for (int j = 0; j < n - 1 - pasada; j++) {
            if (fuera_de_orden(a[j], a[j + 1], orden, m)) {
                intercambiar(&a[j], &a[j + 1], m);
                hubo_intercambio = 1;
            }
        }
        if (!hubo_intercambio) {
            break;  /* optimización: sin intercambios, ya está ordenado */
        }
    }
    return 0;
}

/*
 * SELECTION SORT.
 * En la iteración i se busca, en la parte no ordenada a[i..n-1], la posición
 * del elemento que debe ir en a[i] (el mínimo en ascendente, el máximo en
 * descendente) y se intercambia con a[i]. La búsqueda recorre SIEMPRE toda la
 * parte no ordenada, por eso hace n(n-1)/2 comparaciones aunque el arreglo ya
 * esté ordenado. Realiza como máximo n-1 intercambios.
 */
static int ordenar_seleccion(int *a, int n, Orden orden, Metricas *m)
{
    for (int i = 0; i < n - 1; i++) {
        int indice_elegido = i;

        for (int j = i + 1; j < n; j++) {
            /* Si el elegido está "después" de a[j], a[j] es mejor candidato. */
            if (fuera_de_orden(a[indice_elegido], a[j], orden, m)) {
                indice_elegido = j;
            }
        }
        if (indice_elegido != i) {  /* evita intercambios de un elemento consigo mismo */
            intercambiar(&a[i], &a[indice_elegido], m);
        }
    }
    return 0;
}

/*
 * INSERTION SORT.
 * a[0..i-1] es la parte ordenada. Se guarda la clave a[i], se DESPLAZA una
 * posición a la derecha cada elemento de la parte ordenada que esté después de
 * la clave y se escribe la clave en el hueco. Con datos casi ordenados casi no
 * hay desplazamientos (mejor caso: n-1 comparaciones y 0 movimientos).
 */
static int ordenar_insercion(int *a, int n, Orden orden, Metricas *m)
{
    for (int i = 1; i < n; i++) {
        int clave = a[i];
        int j = i - 1;

        /* El operador && evita acceder a a[-1] y solo cuenta comparaciones reales. */
        while (j >= 0 && fuera_de_orden(a[j], clave, orden, m)) {
            a[j + 1] = a[j];   /* desplazamiento: 1 movimiento */
            m->movimientos++;
            j--;
        }
        if (j + 1 != i) {      /* solo se escribe si la clave cambió de lugar */
            a[j + 1] = clave;
            m->movimientos++;
        }
    }
    return 0;
}

/*
 * MERGE SORT (divide y vencerás).
 *
 * combinar(): mezcla las mitades ya ordenadas a[izq..medio] y a[medio+1..der]
 * en el arreglo auxiliar y luego copia el resultado de vuelta. Se toma el
 * elemento de la derecha SOLO si está estrictamente fuera de orden respecto al
 * de la izquierda; en empates se toma el izquierdo, lo que hace al método
 * estable.
 */
static void combinar(int *a, int *aux, int izq, int medio, int der,
                     Orden orden, Metricas *m)
{
    int i = izq;        /* recorre la mitad izquierda */
    int j = medio + 1;  /* recorre la mitad derecha   */
    int k = izq;        /* posición de escritura en aux */

    while (i <= medio && j <= der) {
        if (fuera_de_orden(a[i], a[j], orden, m)) {
            aux[k++] = a[j++];
        } else {
            aux[k++] = a[i++];
        }
        m->movimientos++;
    }
    while (i <= medio) {  /* sobrantes de la izquierda */
        aux[k++] = a[i++];
        m->movimientos++;
    }
    while (j <= der) {    /* sobrantes de la derecha */
        aux[k++] = a[j++];
        m->movimientos++;
    }
    for (k = izq; k <= der; k++) {  /* copia de vuelta al arreglo original */
        a[k] = aux[k];
        m->movimientos++;
    }
}

/* Divide recursivamente a[izq..der] y combina las mitades ordenadas. */
static void mezcla_recursiva(int *a, int *aux, int izq, int der,
                             Orden orden, Metricas *m)
{
    if (izq >= der) {
        return;  /* caso base: 0 o 1 elemento ya está ordenado */
    }
    int medio = izq + (der - izq) / 2;  /* evita desbordamiento de izq+der */

    mezcla_recursiva(a, aux, izq, medio, orden, m);
    mezcla_recursiva(a, aux, medio + 1, der, orden, m);
    combinar(a, aux, izq, medio, der, orden, m);
}

/* Envoltorio: reserva UNA sola vez el arreglo auxiliar de n elementos. */
static int ordenar_mezcla(int *a, int n, Orden orden, Metricas *m)
{
    if (n <= 1) {
        return 0;  /* caso límite: nada que ordenar */
    }
    int *aux = malloc((size_t)n * sizeof *aux);
    if (aux == NULL) {
        return -1;
    }
    mezcla_recursiva(a, aux, 0, n - 1, orden, m);
    free(aux);
    return 0;
}

/* Tabla de algoritmos disponibles (el orden coincide con el menú). */
static const Algoritmo ALGORITMOS[NUM_ALGORITMOS] = {
    {"Bubble Sort",    ordenar_burbuja,   1},
    {"Selection Sort", ordenar_seleccion, 1},
    {"Insertion Sort", ordenar_insercion, 0},
    {"Merge Sort",     ordenar_mezcla,    0}
};

/* ============================================================================
 *  ENTRADA DE DATOS CON VALIDACIÓN
 * ========================================================================== */

/*
 * Lee una línea completa de stdin en 'buffer'.
 * Devuelve 1 si se leyó bien, 0 si se llegó al fin de la entrada (EOF) y -1 si
 * la línea no cabía en el buffer (el resto de la línea se descarta).
 */
static int leer_linea(char *buffer, size_t tamano)
{
    if (fgets(buffer, (int)tamano, stdin) == NULL) {
        return 0;
    }
    size_t largo = strlen(buffer);
    if (largo > 0 && buffer[largo - 1] == '\n') {
        buffer[largo - 1] = '\0';
        return 1;
    }
    if (feof(stdin)) {
        return 1;  /* última línea sin salto de línea */
    }
    int c;
    while ((c = getchar()) != '\n' && c != EOF) {
        /* descarta el resto de la línea demasiado larga */
    }
    return -1;
}

/* Convierte un entero con strtol. Devuelve 1 si hubo conversión sin desborde. */
static int convertir_entero(const char *texto, char **fin, long *valor)
{
    char *final = NULL;
    errno = 0;
    long v = strtol(texto, &final, 10);
    if (final == texto || errno == ERANGE) {
        return 0;
    }
    *fin = final;
    *valor = v;
    return 1;
}

/*
 * Pide un entero en el rango [minimo, maximo] y repite hasta que sea válido.
 * Devuelve 1 si se obtuvo el valor y 0 si se acabó la entrada (EOF).
 */
static int leer_entero(const char *mensaje, long minimo, long maximo,
                       long *resultado)
{
    char buffer[128];

    for (;;) {
        printf("%s", mensaje);
        fflush(stdout);

        int estado = leer_linea(buffer, sizeof buffer);
        if (estado == 0) {
            return 0;
        }
        if (estado < 0) {
            puts("Error: entrada demasiado larga.");
            continue;
        }

        char *fin = NULL;
        long valor = 0;
        if (!convertir_entero(buffer, &fin, &valor)) {
            puts("Error: ingrese un numero entero valido.");
            continue;
        }
        while (isspace((unsigned char)*fin)) {
            fin++;
        }
        if (*fin != '\0') {
            puts("Error: hay caracteres no validos despues del numero.");
            continue;
        }
        if (valor < minimo || valor > maximo) {
            printf("Error: el valor debe estar entre %ld y %ld.\n", minimo, maximo);
            continue;
        }
        *resultado = valor;
        return 1;
    }
}

/*
 * Lee exactamente 'n' enteros separados por espacios (se admiten varias
 * líneas). Si una línea contiene un valor inválido o sobran valores, se
 * rechaza SOLO esa línea y se vuelve a pedir. Devuelve 1 si todo salió bien
 * y 0 si se acabó la entrada.
 */
static int leer_valores(int *destino, int n)
{
    static char buffer[TAM_BUFFER_LINEA];
    int cargados = 0;

    if (n == 0) {
        return 1;
    }
    printf("Ingrese %d valor(es) entero(s) separados por espacios "
           "(puede usar varias lineas):\n", n);

    while (cargados < n) {
        int estado = leer_linea(buffer, sizeof buffer);
        if (estado == 0) {
            return 0;
        }
        if (estado < 0) {
            puts("Error: linea demasiado larga; repita esa linea.");
            continue;
        }

        int antes = cargados;   /* para deshacer si la línea es inválida */
        int error = 0;
        const char *p = buffer;

        for (;;) {
            while (isspace((unsigned char)*p)) {
                p++;
            }
            if (*p == '\0') {
                break;
            }
            char *fin = NULL;
            long valor = 0;
            if (!convertir_entero(p, &fin, &valor) ||
                (*fin != '\0' && !isspace((unsigned char)*fin))) {
                error = 1;
                break;
            }
            if (valor < INT_MIN || valor > INT_MAX) {
                error = 2;
                break;
            }
            if (cargados >= n) {
                error = 3;
                break;
            }
            destino[cargados++] = (int)valor;
            p = fin;
        }

        if (error == 1) {
            puts("Error: se encontro un valor que no es un entero valido.");
        } else if (error == 2) {
            puts("Error: un valor esta fuera del rango de int.");
        } else if (error == 3) {
            printf("Error: se ingresaron mas de %d valores.\n", n);
        }
        if (error) {
            cargados = antes;   /* se descarta toda la línea */
            printf("Repita esa linea (faltan %d valores).\n", n - cargados);
        } else if (cargados < n) {
            printf("Faltan %d valores.\n", n - cargados);
        }
    }
    return 1;
}

/* ============================================================================
 *  UTILIDADES SOBRE ARREGLOS
 * ========================================================================== */

/* Reserva un arreglo de n elementos (al menos 1 byte útil, incluso si n = 0). */
static int arreglo_reservar(Arreglo *arreglo, int n)
{
    arreglo->datos = malloc((size_t)(n > 0 ? n : 1) * sizeof *arreglo->datos);
    arreglo->n = (arreglo->datos != NULL) ? n : 0;
    return arreglo->datos != NULL;
}

static void arreglo_liberar(Arreglo *arreglo)
{
    free(arreglo->datos);
    arreglo->datos = NULL;
    arreglo->n = 0;
}

/* Crea una copia exacta de 'origen' en 'destino'. */
static int arreglo_copiar(Arreglo *destino, const Arreglo *origen)
{
    if (!arreglo_reservar(destino, origen->n)) {
        return 0;
    }
    if (origen->n > 0) {
        memcpy(destino->datos, origen->datos,
               (size_t)origen->n * sizeof *origen->datos);
    }
    return 1;
}

/* Imprime un arreglo; si es largo, solo los extremos. */
static void imprimir_arreglo(const char *titulo, const int *d, int n)
{
    printf("%s (n = %d): [", titulo, n);
    if (n <= MAX_IMPRESION) {
        for (int i = 0; i < n; i++) {
            printf(i == 0 ? "%d" : ", %d", d[i]);
        }
    } else {
        for (int i = 0; i < EXTREMOS_IMPRESION; i++) {
            printf(i == 0 ? "%d" : ", %d", d[i]);
        }
        printf(", ... , ");
        for (int i = n - EXTREMOS_IMPRESION; i < n; i++) {
            printf(i == n - EXTREMOS_IMPRESION ? "%d" : ", %d", d[i]);
        }
    }
    puts("]");
}

static int comparar_asc(const void *x, const void *y)
{
    int a = *(const int *)x;
    int b = *(const int *)y;
    return (a > b) - (a < b);
}

static int comparar_desc(const void *x, const void *y)
{
    return comparar_asc(y, x);
}

/*
 * Verifica un resultado: debe ser IGUAL a la salida de qsort() sobre los datos
 * originales (lo que comprueba a la vez el orden y que sea una permutación).
 * Devuelve 1 si es correcto, 0 si no, -1 si no se pudo verificar.
 */
static int verificar_resultado(const int *resultado, const int *original, int n,
                               Orden orden)
{
    Arreglo referencia = {NULL, 0};
    Arreglo origen = {(int *)original, n};

    if (!arreglo_copiar(&referencia, &origen)) {
        return -1;
    }
    qsort(referencia.datos, (size_t)n, sizeof(int),
          orden == ASCENDENTE ? comparar_asc : comparar_desc);

    int correcto = (n == 0) ||
                   memcmp(referencia.datos, resultado,
                          (size_t)n * sizeof(int)) == 0;
    arreglo_liberar(&referencia);
    return correcto;
}

/* ============================================================================
 *  GENERACIÓN DE DATOS DE PRUEBA
 * ========================================================================== */

/* Entero pseudoaleatorio en [minimo, maximo]. */
static int aleatorio_en_rango(int minimo, int maximo)
{
    return minimo + rand() % (maximo - minimo + 1);
}

/*
 * Rellena 'd' según el patrón. "Ordenado" e "inverso" se refieren al orden
 * ASCENDENTE: son mejor y peor caso cuando se ordena de forma ascendente.
 */
static void generar_datos(int *d, int n, Patron patron)
{
    for (int i = 0; i < n; i++) {
        d[i] = aleatorio_en_rango(ALEATORIO_MIN, ALEATORIO_MAX);
    }
    if (patron == PATRON_ALEATORIO) {
        return;
    }

    qsort(d, (size_t)n, sizeof(int), comparar_asc);

    if (patron == PATRON_INVERSO) {
        for (int i = 0, j = n - 1; i < j; i++, j--) {
            int t = d[i];
            d[i] = d[j];
            d[j] = t;
        }
    } else if (patron == PATRON_CASI_ORDENADO && n >= 2) {
        /* Desordena ligeramente: n/20 intercambios al azar (al menos uno). */
        int cantidad = n / 20 > 0 ? n / 20 : 1;
        for (int k = 0; k < cantidad; k++) {
            int i = rand() % n;
            int j = rand() % n;
            int t = d[i];
            d[i] = d[j];
            d[j] = t;
        }
    }
}

/* ============================================================================
 *  EJECUCIÓN Y MEDICIÓN
 * ========================================================================== */

/*
 * Ejecuta un algoritmo sobre una COPIA de 'original' y deja el resultado en
 * 'salida' (que el llamador debe liberar). Solo se mide con clock() la llamada
 * al algoritmo; la copia, la verificación y la impresión quedan fuera.
 * Devuelve 1 si se pudo ejecutar y 0 si falló la reserva de memoria.
 */
static int ejecutar_algoritmo(const Algoritmo *algoritmo, const Arreglo *original,
                              Orden orden, Arreglo *salida, Resultado *resultado)
{
    memset(resultado, 0, sizeof *resultado);
    resultado->verificacion = -1;

    if (!arreglo_copiar(salida, original)) {
        return 0;
    }

    clock_t inicio = clock();
    resultado->estado = algoritmo->ordenar(salida->datos, salida->n, orden,
                                           &resultado->metricas);
    clock_t fin = clock();

    resultado->tiempo_ms = (double)(fin - inicio) * 1000.0 / CLOCKS_PER_SEC;

    if (resultado->estado == 0) {
        resultado->verificacion = verificar_resultado(salida->datos,
                                                      original->datos,
                                                      original->n, orden);
    }
    return 1;
}

static const char *texto_verificacion(int verificacion)
{
    return verificacion == 1 ? "OK" : (verificacion == 0 ? "ERROR" : "no hecha");
}

static void aviso_tiempos(int n)
{
    if (n < TAM_MIN_TIEMPO) {
        printf("Nota: con n < %d los tiempos son demasiado breves (clock() tiene "
               "poca resolucion);\n      no son fiables para comparar. Use datos "
               "generados con n grande.\n", TAM_MIN_TIEMPO);
    }
}

static void imprimir_definiciones(void)
{
    puts("\nDefinicion de las metricas:");
    puts("  Comparacion : evaluacion de la relacion de orden entre dos elementos");
    puts("                (no se cuentan las comparaciones de indices de bucles).");
    puts("  Intercambio : permuta de dos posiciones (solo Bubble y Selection);");
    puts("                cada intercambio equivale a 2 movimientos.");
    puts("  Movimiento  : escritura de un elemento en el arreglo o en el auxiliar");
    puts("                (Insertion: desplazamientos + colocacion de la clave;");
    puts("                 Merge: copia al auxiliar + copia de regreso).");
    puts("  Tiempo      : clock() alrededor de la llamada al algoritmo (CPU, ms).");
}

/* Opción del menú: ejecutar un solo algoritmo y mostrar su resultado. */
static void ejecutar_uno(const Arreglo *original, Orden orden)
{
    long eleccion = 0;
    printf("\n1) Bubble Sort  2) Selection Sort  3) Insertion Sort  4) Merge Sort\n");
    if (!leer_entero("Algoritmo (1-4): ", 1, NUM_ALGORITMOS, &eleccion)) {
        return;
    }
    const Algoritmo *algoritmo = &ALGORITMOS[eleccion - 1];

    if (original->n > TAM_AVISO_LENTO && algoritmo->usa_intercambios) {
        printf("Aviso: %s es O(n^2); con n = %d puede tardar varios segundos.\n",
               algoritmo->nombre, original->n);
    }

    Arreglo salida = {NULL, 0};
    Resultado r;
    if (!ejecutar_algoritmo(algoritmo, original, orden, &salida, &r) || r.estado != 0) {
        puts("Error: no hay memoria suficiente para ejecutar el algoritmo.");
        arreglo_liberar(&salida);
        return;
    }

    printf("\n=== %s (%s) ===\n", algoritmo->nombre,
           orden == ASCENDENTE ? "ascendente" : "descendente");
    imprimir_arreglo("Original", original->datos, original->n);
    imprimir_arreglo("Ordenado", salida.datos, salida.n);
    printf("Comparaciones : %llu\n", r.metricas.comparaciones);
    if (algoritmo->usa_intercambios) {
        printf("Intercambios  : %llu\n", r.metricas.intercambios);
    }
    printf("Movimientos   : %llu\n", r.metricas.movimientos);
    printf("Tiempo        : %.3f ms\n", r.tiempo_ms);
    printf("Verificacion  : %s (contra qsort)\n", texto_verificacion(r.verificacion));
    aviso_tiempos(original->n);
    arreglo_liberar(&salida);
}

/* Opción del menú: los cuatro algoritmos sobre copias idénticas de los datos. */
static void comparar_algoritmos(const Arreglo *original, Orden orden)
{
    Arreglo salidas[NUM_ALGORITMOS] = {{NULL, 0}, {NULL, 0}, {NULL, 0}, {NULL, 0}};
    Resultado resultados[NUM_ALGORITMOS];
    int completo = 1;

    if (original->n > TAM_AVISO_LENTO) {
        printf("Aviso: Bubble y Selection son O(n^2); con n = %d pueden tardar "
               "varios segundos.\n", original->n);
    }

    for (int i = 0; i < NUM_ALGORITMOS && completo; i++) {
        if (!ejecutar_algoritmo(&ALGORITMOS[i], original, orden, &salidas[i],
                                &resultados[i]) || resultados[i].estado != 0) {
            puts("Error: no hay memoria suficiente para la comparacion.");
            completo = 0;
        }
    }

    if (completo) {
        printf("\n=== Comparacion (%s) ===\n",
               orden == ASCENDENTE ? "orden ascendente" : "orden descendente");
        imprimir_arreglo("Original", original->datos, original->n);

        puts("\n+----------------+---------------+--------------+-------------+"
             "-------------+------------+");
        puts("| Algoritmo      | Comparaciones | Intercambios | Movimientos |"
             " Tiempo (ms) | Verificado |");
        puts("+----------------+---------------+--------------+-------------+"
             "-------------+------------+");
        for (int i = 0; i < NUM_ALGORITMOS; i++) {
            char texto_intercambios[32];
            if (ALGORITMOS[i].usa_intercambios) {
                snprintf(texto_intercambios, sizeof texto_intercambios, "%llu",
                         resultados[i].metricas.intercambios);
            } else {
                snprintf(texto_intercambios, sizeof texto_intercambios, "-");
            }
            printf("| %-14s | %13llu | %12s | %11llu | %11.3f | %-10s |\n",
                   ALGORITMOS[i].nombre,
                   resultados[i].metricas.comparaciones,
                   texto_intercambios,
                   resultados[i].metricas.movimientos,
                   resultados[i].tiempo_ms,
                   texto_verificacion(resultados[i].verificacion));
        }
        puts("+----------------+---------------+--------------+-------------+"
             "-------------+------------+");
        puts("('-' = el metodo no usa intercambios: solo desplazamientos/copias.)");

        puts("\nResultado ordenado de cada algoritmo:");
        for (int i = 0; i < NUM_ALGORITMOS; i++) {
            char titulo[32];
            snprintf(titulo, sizeof titulo, "%-14s", ALGORITMOS[i].nombre);
            imprimir_arreglo(titulo, salidas[i].datos, salidas[i].n);
        }
        aviso_tiempos(original->n);
    }

    for (int i = 0; i < NUM_ALGORITMOS; i++) {
        arreglo_liberar(&salidas[i]);
    }
}

/* ============================================================================
 *  CARGA DE DATOS DESDE EL MENÚ
 * ========================================================================== */

/* Opción 1: entrada manual validada. Devuelve 0 solo si se acabó la entrada. */
static int cargar_manual(Arreglo *original)
{
    long n = 0;
    char mensaje[80];
    snprintf(mensaje, sizeof mensaje,
             "Cantidad de elementos (0 a %d): ", MAX_MANUAL);
    if (!leer_entero(mensaje, 0, MAX_MANUAL, &n)) {
        return 0;
    }

    Arreglo nuevo = {NULL, 0};
    if (!arreglo_reservar(&nuevo, (int)n)) {
        puts("Error: no hay memoria suficiente.");
        return 1;
    }
    if (!leer_valores(nuevo.datos, nuevo.n)) {
        arreglo_liberar(&nuevo);
        return 0;
    }
    arreglo_liberar(original);
    *original = nuevo;
    puts("Arreglo cargado correctamente.");
    return 1;
}

/* Opción 2: generación de datos de prueba. Devuelve 0 solo si se acabó la entrada. */
static int cargar_generado(Arreglo *original)
{
    long n = 0, tipo = 0, semilla = 0;
    char mensaje[80];

    snprintf(mensaje, sizeof mensaje,
             "Cantidad de elementos (0 a %d): ", MAX_ELEMENTOS);
    if (!leer_entero(mensaje, 0, MAX_ELEMENTOS, &n)) {
        return 0;
    }
    puts("Tipo de datos: 1) Aleatorios  2) Ya ordenados (asc.)  "
         "3) Orden inverso  4) Casi ordenados");
    if (!leer_entero("Tipo (1-4): ", 1, 4, &tipo)) {
        return 0;
    }
    if (!leer_entero("Semilla (0 = usar la hora actual): ", 0, 2147483647L, &semilla)) {
        return 0;
    }
    if (semilla == 0) {
        semilla = (long)(time(NULL) % 2147483647L);
        if (semilla == 0) {
            semilla = 1;
        }
    }
    srand((unsigned int)semilla);
    printf("Semilla utilizada: %ld (repitala para obtener los mismos datos).\n",
           semilla);

    Arreglo nuevo = {NULL, 0};
    if (!arreglo_reservar(&nuevo, (int)n)) {
        puts("Error: no hay memoria suficiente.");
        return 1;
    }
    generar_datos(nuevo.datos, nuevo.n, (Patron)tipo);
    arreglo_liberar(original);
    *original = nuevo;
    printf("Se genero un arreglo de %d elementos.\n", original->n);
    return 1;
}

/* ============================================================================
 *  MENÚ PRINCIPAL
 * ========================================================================== */

static void mostrar_menu(const Arreglo *original, Orden orden)
{
    printf("\n================ ALGORITMOS DE ORDENAMIENTO ================\n");
    printf("Arreglo actual: %d elementos | Orden: %s\n", original->n,
           orden == ASCENDENTE ? "ascendente" : "descendente");
    puts("  1. Ingresar un arreglo manualmente");
    puts("  2. Generar un arreglo de prueba (aleatorio, ordenado, inverso...)");
    puts("  3. Mostrar el arreglo actual");
    puts("  4. Cambiar el orden (ascendente / descendente)");
    puts("  5. Ejecutar UN algoritmo");
    puts("  6. Comparar los CUATRO algoritmos con los mismos datos");
    puts("  7. Ver definicion de las metricas");
    puts("  0. Salir");
}

int main(void)
{
    /* Arreglo de ejemplo precargado (el mismo del informe). */
    static const int EJEMPLO[] = {35, 12, 48, 7, 19, 3, 26};
    const int n_ejemplo = (int)(sizeof EJEMPLO / sizeof EJEMPLO[0]);

    Arreglo original = {NULL, 0};
    Orden orden = ASCENDENTE;

    if (!arreglo_reservar(&original, n_ejemplo)) {
        puts("Error: no hay memoria suficiente.");
        return EXIT_FAILURE;
    }
    memcpy(original.datos, EJEMPLO, sizeof EJEMPLO);

    int continuar = 1;
    while (continuar) {
        mostrar_menu(&original, orden);

        long opcion = 0;
        if (!leer_entero("Opcion: ", 0, 7, &opcion)) {
            puts("\nFin de la entrada. Hasta luego.");
            break;
        }

        switch (opcion) {
        case 1:
            continuar = cargar_manual(&original);
            break;
        case 2:
            continuar = cargar_generado(&original);
            break;
        case 3:
            imprimir_arreglo("Arreglo actual", original.datos, original.n);
            break;
        case 4:
            orden = (orden == ASCENDENTE) ? DESCENDENTE : ASCENDENTE;
            printf("Orden cambiado a: %s\n",
                   orden == ASCENDENTE ? "ascendente" : "descendente");
            break;
        case 5:
            ejecutar_uno(&original, orden);
            break;
        case 6:
            comparar_algoritmos(&original, orden);
            break;
        case 7:
            imprimir_definiciones();
            break;
        case 0:
            continuar = 0;
            break;
        default:
            break;  /* no ocurre: leer_entero ya valida el rango */
        }
        if (!continuar && opcion != 0) {
            puts("\nFin de la entrada. Hasta luego.");
        }
    }

    arreglo_liberar(&original);
    return EXIT_SUCCESS;
}