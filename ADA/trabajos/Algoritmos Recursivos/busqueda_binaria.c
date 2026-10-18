/* busqueda_binaria.c - Busqueda binaria recursiva en un arreglo ordenado */
#include <stdio.h>

#define TAM_MAX 100

/* Verifica que el arreglo este ordenado de forma ascendente. */
int esta_ordenado(const int arr[], int n) {
    int i;
    for (i = 1; i < n; i++) {
        if (arr[i - 1] > arr[i]) {
            return 0;
        }
    }
    return 1;
}

/* Busca 'x' en arr[inicio..fin]. Devuelve el indice o -1 si no existe.
   Caso base 1: inicio > fin (rango vacio) -> -1
   Caso base 2: arr[medio] == x -> medio
   Caso recursivo: se descarta la mitad donde x no puede estar. */
int busqueda_binaria(const int arr[], int inicio, int fin, int x) {
    int medio;

    if (inicio > fin) {
        return -1;                        /* no encontrado */
    }
    medio = inicio + (fin - inicio) / 2;  /* evita desbordamiento de int */
    if (arr[medio] == x) {
        return medio;                     /* encontrado */
    }
    if (x < arr[medio]) {
        return busqueda_binaria(arr, inicio, medio - 1, x);
    }
    return busqueda_binaria(arr, medio + 1, fin, x);
}

int main(void) {
    int arr[TAM_MAX], n, x, i, pos;

    printf("Tamano del arreglo (1 a %d): ", TAM_MAX);
    if (scanf("%d", &n) != 1 || n < 1 || n > TAM_MAX) {
        printf("Error: tamano no valido.\n");
        return 1;
    }
    printf("Ingrese %d enteros en orden ascendente: ", n);
    for (i = 0; i < n; i++) {
        if (scanf("%d", &arr[i]) != 1) {
            printf("Error: entrada no valida.\n");
            return 1;
        }
    }
    if (!esta_ordenado(arr, n)) {
        printf("Error: el arreglo debe estar ordenado ascendentemente.\n");
        return 1;
    }
    printf("Elemento a buscar: ");
    if (scanf("%d", &x) != 1) {
        printf("Error: entrada no valida.\n");
        return 1;
    }
    pos = busqueda_binaria(arr, 0, n - 1, x);
    if (pos >= 0) {
        printf("Elemento %d encontrado en la posicion %d.\n", x, pos);
    } else {
        printf("Elemento %d no encontrado.\n", x);
    }
    return 0;
}
