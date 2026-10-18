/* fibonacci.c - Primeros N terminos de la serie de Fibonacci (recursivo) */
#include <stdio.h>

#define N_MAX 35  /* limite: la version recursiva simple es exponencial */

/* Casos base: fib(0) = 0 y fib(1) = 1
   Caso recursivo: fib(n) = fib(n - 1) + fib(n - 2) */
unsigned long long fibonacci(int n) {
    if (n == 0) {
        return 0ULL;                      /* caso base 1 */
    }
    if (n == 1) {
        return 1ULL;                      /* caso base 2 */
    }
    return fibonacci(n - 1) + fibonacci(n - 2);  /* caso recursivo */
}

int main(void) {
    int n, i;

    printf("Cantidad de terminos (1 a %d): ", N_MAX);
    if (scanf("%d", &n) != 1) {
        printf("Error: entrada no valida.\n");
        return 1;
    }
    if (n < 1 || n > N_MAX) {
        printf("Error: N debe estar entre 1 y %d.\n", N_MAX);
        return 1;
    }
    printf("Serie de Fibonacci (%d terminos):\n", n);
    for (i = 0; i < n; i++) {
        printf("%llu%s", fibonacci(i), (i < n - 1) ? ", " : "\n");
    }
    return 0;
}
