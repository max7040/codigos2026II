/* factorial.c - Factorial de un numero mediante recursividad */
#include <stdio.h>

#define N_MAX 20  /* 20! = 2432902008176640000 cabe en unsigned long long */

/* Caso base: n == 0 (o n == 1) -> 1
   Caso recursivo: n! = n * (n - 1)! */
unsigned long long factorial(int n) {
    if (n <= 1) {
        return 1ULL;                      /* caso base */
    }
    return (unsigned long long)n * factorial(n - 1);  /* caso recursivo */
}

int main(void) {
    int n;

    printf("Ingrese un entero entre 0 y %d: ", N_MAX);
    if (scanf("%d", &n) != 1) {           /* valida que sea un entero */
        printf("Error: entrada no valida.\n");
        return 1;
    }
    if (n < 0) {
        printf("Error: el factorial no esta definido para negativos.\n");
        return 1;
    }
    if (n > N_MAX) {                      /* evita desbordamiento */
        printf("Error: n debe ser menor o igual que %d.\n", N_MAX);
        return 1;
    }
    printf("%d! = %llu\n", n, factorial(n));
    return 0;
}
