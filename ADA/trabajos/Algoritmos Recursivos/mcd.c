/* mcd.c - Maximo comun divisor con el algoritmo de Euclides recursivo */
#include <stdio.h>

/* Caso base: b == 0 -> mcd(a, 0) = a
   Caso recursivo: mcd(a, b) = mcd(b, a % b)
   Termina porque el segundo argumento (a % b) es siempre menor que b. */
long long mcd(long long a, long long b) {
    if (b == 0) {
        return a;                         /* caso base */
    }
    return mcd(b, a % b);                 /* caso recursivo */
}

int main(void) {
    long long a, b;

    printf("Ingrese dos enteros no negativos (a b): ");
    if (scanf("%lld %lld", &a, &b) != 2) {
        printf("Error: entrada no valida.\n");
        return 1;
    }
    if (a < 0 || b < 0) {
        printf("Error: los numeros deben ser no negativos.\n");
        return 1;
    }
    if (a == 0 && b == 0) {
        printf("Error: mcd(0, 0) no esta definido.\n");
        return 1;
    }
    printf("mcd(%lld, %lld) = %lld\n", a, b, mcd(a, b));
    return 0;
}
