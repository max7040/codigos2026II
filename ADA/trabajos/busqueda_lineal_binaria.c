/*
 * busquedas.c
 * Implementacion de busqueda lineal y busqueda binaria iterativa.
 * Estandar: C11.
 * Compilacion: gcc -std=c11 -Wall -Wextra -pedantic -o busquedas busquedas.c
 *
 * Convencion de posiciones: se usan INDICES DESDE 0 (el primer elemento
 * tiene indice 0). Si el elemento no existe, las funciones devuelven -1.
 *
 * Convencion de conteo: se cuenta una comparacion cada vez que se
 * contrasta un elemento del arreglo con la clave buscada. En la busqueda
 * binaria se cuenta una comparacion por iteracion (comparacion de tres
 * vias entre arr[medio] y la clave).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <limits.h>

#define TAM 15
#define BUFFER 64

/* Busqueda lineal: recorre el arreglo de izquierda a derecha.
 * Parametros: arr (arreglo), n (tamano), clave (valor buscado),
 *             comparaciones (salida: numero de comparaciones).
 * Retorna: indice de la clave o -1 si no existe. */
int busqueda_lineal(const int arr[], int n, int clave, int *comparaciones)
{
    *comparaciones = 0;
    for (int i = 0; i < n; i++) {
        (*comparaciones)++;
        if (arr[i] == clave) {
            return i;
        }
    }
    return -1;
}

/* Busqueda binaria iterativa: REQUIERE arreglo ordenado ascendentemente.
 * Retorna: indice de la clave o -1 si no existe. */
int busqueda_binaria(const int arr[], int n, int clave, int *comparaciones)
{
    int izq = 0;
    int der = n - 1;
    *comparaciones = 0;

    while (izq <= der) {
        /* Punto medio sin desbordamiento: evita (izq + der) / 2 */
        int medio = izq + (der - izq) / 2;
        (*comparaciones)++;
        if (arr[medio] == clave) {
            return medio;
        } else if (arr[medio] < clave) {
            izq = medio + 1;      /* descartar mitad izquierda */
        } else {
            der = medio - 1;      /* descartar mitad derecha */
        }
    }
    return -1;
}

/* Lee un entero validado desde la entrada estandar.
 * Retorna 1 si se leyo correctamente, 0 si se llego a fin de entrada. */
static int leer_entero(const char *mensaje, int *valor)
{
    char buf[BUFFER];
    char *fin;

    for (;;) {
        printf("%s", mensaje);
        if (fgets(buf, sizeof buf, stdin) == NULL) {
            return 0;
        }
        errno = 0;
        long v = strtol(buf, &fin, 10);
        if (fin == buf || errno == ERANGE || v > INT_MAX || v < INT_MIN) {
            printf("Entrada invalida. Ingrese un numero entero.\n");
            continue;
        }
        while (*fin == ' ' || *fin == '\t') fin++;
        if (*fin != '\n' && *fin != '\0') {
            printf("Entrada invalida. Ingrese un numero entero.\n");
            continue;
        }
        *valor = (int)v;
        return 1;
    }
}

static void mostrar_resultado(const char *nombre, int pos, int comp)
{
    if (pos >= 0) {
        printf("%-16s: encontrado en el indice %d (%d comparaciones)\n",
               nombre, pos, comp);
    } else {
        printf("%-16s: el elemento NO existe (%d comparaciones)\n",
               nombre, comp);
    }
}

int main(void)
{
    /* Arreglo de prueba ORDENADO ascendentemente (necesario para binaria) */
    const int datos[TAM] = {3, 8, 12, 17, 21, 25, 30, 34,
                            42, 47, 53, 58, 64, 71, 89};
    int opcion, clave, pos, comp;

    printf("Arreglo (indices desde 0):\n");
    for (int i = 0; i < TAM; i++) {
        printf("[%d]=%d%s", i, datos[i], (i < TAM - 1) ? "  " : "\n");
    }

    for (;;) {
        printf("\n=== MENU ===\n1. Busqueda lineal\n2. Busqueda binaria\n"
               "3. Ambas (comparar)\n0. Salir\n");
        if (!leer_entero("Elija una opcion: ", &opcion)) break;
        if (opcion == 0) break;
        if (opcion < 1 || opcion > 3) {
            printf("Opcion fuera de rango (0-3).\n");
            continue;
        }
        if (!leer_entero("Numero a buscar: ", &clave)) break;

        if (opcion == 1 || opcion == 3) {
            pos = busqueda_lineal(datos, TAM, clave, &comp);
            mostrar_resultado("Busqueda lineal", pos, comp);
        }
        if (opcion == 2 || opcion == 3) {
            pos = busqueda_binaria(datos, TAM, clave, &comp);
            mostrar_resultado("Busqueda binaria", pos, comp);
        }
    }
    printf("Fin del programa.\n");
    return 0;
}
