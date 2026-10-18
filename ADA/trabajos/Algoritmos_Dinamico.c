/*
 * programacion_dinamica.c
 * Curso: Analisis y Desarrollo de Algoritmos - UNA Puno
 * Autor: Ali Maximo Huisa Quispe
 *
 * Tres algoritmos de Programacion Dinamica:
 *   1. Multiplicacion de Cadenas de Matrices (MCM) con reconstruccion
 *   2. Subsecuencia Comun Mas Larga (LCS)
 *   3. Rutas mas cortas entre todos los pares (Floyd-Warshall)
 *
 * Compilar: gcc -Wall -Wextra -std=c99 -o pd programacion_dinamica.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

/* ====================================================================
 * 1. MULTIPLICACION DE CADENAS DE MATRICES
 *    A_i tiene dimensiones p[i-1] x p[i], i = 1..n
 *    m[i][j] = costo minimo de calcular A_i ... A_j
 *    s[i][j] = punto de ruptura k optimo (A_i..A_k)(A_{k+1}..A_j)
 * ==================================================================== */
#define MAX_N 32

long long mcm(const int p[], int n,
              long long m[][MAX_N + 1], int s[][MAX_N + 1])
{
    int i, j, k, L;

    for (i = 1; i <= n; i++)
        m[i][i] = 0;                       /* caso base: una matriz */

    for (L = 2; L <= n; L++) {             /* L = longitud de la cadena */
        for (i = 1; i <= n - L + 1; i++) {
            j = i + L - 1;
            m[i][j] = LLONG_MAX;
            for (k = i; k < j; k++) {      /* probar cada punto de ruptura */
                long long q = m[i][k] + m[k + 1][j]
                            + (long long)p[i - 1] * p[k] * p[j];
                if (q < m[i][j]) {
                    m[i][j] = q;
                    s[i][j] = k;
                }
            }
        }
    }
    return m[1][n];
}

/* Imprime la parentizacion optima recorriendo la tabla s */
void imprimir_parentesis(int s[][MAX_N + 1], int i, int j)
{
    if (i == j) {
        printf("A%d", i);
    } else {
        printf("(");
        imprimir_parentesis(s, i, s[i][j]);
        printf(" x ");
        imprimir_parentesis(s, s[i][j] + 1, j);
        printf(")");
    }
}

void probar_mcm(const int p[], int n)
{
    static long long m[MAX_N + 1][MAX_N + 1];
    static int s[MAX_N + 1][MAX_N + 1];
    int i;

    printf("Dimensiones: ");
    for (i = 0; i <= n; i++) printf("%d ", p[i]);
    printf("\nCosto minimo (multiplicaciones escalares): %lld\n",
           mcm(p, n, m, s));
    printf("Parentizacion optima: ");
    imprimir_parentesis(s, 1, n);
    printf("\n\n");
}

/* ====================================================================
 * 2. SUBSECUENCIA COMUN MAS LARGA (LCS)
 *    c[i][j] = longitud de la LCS de x[0..i-1] y y[0..j-1]
 *    Tiempo y espacio: O(n1 * n2)
 * ==================================================================== */
#define C(i, j) c[(i) * (n2 + 1) + (j)]

/* Devuelve la LCS en memoria dinamica (el llamador debe hacer free) */
char *lcs(const char *x, const char *y, int *longitud)
{
    int n1 = (int)strlen(x), n2 = (int)strlen(y);
    int i, j, len;
    int *c = calloc((size_t)(n1 + 1) * (n2 + 1), sizeof(int));
    char *res;

    if (!c) return NULL;

    for (i = 1; i <= n1; i++) {
        for (j = 1; j <= n2; j++) {
            if (x[i - 1] == y[j - 1])
                C(i, j) = C(i - 1, j - 1) + 1;
            else
                C(i, j) = (C(i - 1, j) >= C(i, j - 1)) ? C(i - 1, j)
                                                       : C(i, j - 1);
        }
    }

    /* Reconstruccion hacia atras */
    len = C(n1, n2);
    res = malloc((size_t)len + 1);
    if (!res) { free(c); return NULL; }
    res[len] = '\0';
    i = n1; j = n2;
    while (i > 0 && j > 0) {
        if (x[i - 1] == y[j - 1]) {
            res[--len] = x[i - 1];
            i--; j--;
        } else if (C(i - 1, j) >= C(i, j - 1)) {
            i--;
        } else {
            j--;
        }
    }

    *longitud = C(n1, n2);
    free(c);
    return res;
}

void probar_lcs(const char *x, const char *y)
{
    int len = 0;
    char *r = lcs(x, y, &len);
    if (!r) { fprintf(stderr, "Sin memoria\n"); return; }
    printf("X = \"%s\"\nY = \"%s\"\n", x, y);
    printf("Longitud LCS = %d, LCS = \"%s\"\n\n", len, r);
    free(r);
}

/* ====================================================================
 * 3. FLOYD-WARSHALL (todos los pares)
 *    D^(k)(i,j) = costo del camino mas corto de i a j usando solo
 *    vertices intermedios en {0..k-1}.
 *    Recurrencia:
 *      D^(k)(i,j) = min( D^(k-1)(i,j), D^(k-1)(i,k) + D^(k-1)(k,j) )
 *    Como la fila y columna k no cambian durante la iteracion k,
 *    basta UNA matriz: espacio O(n^2) en lugar de O(n^3).
 * ==================================================================== */
#define MAXV 10
#define INF  (INT_MAX / 2)

void imprimir_matriz(const char *titulo, int n, int D[][MAXV])
{
    int i, j;
    printf("%s\n", titulo);
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            if (D[i][j] >= INF) printf("%5s", "INF");
            else                printf("%5d", D[i][j]);
        }
        printf("\n");
    }
    printf("\n");
}

/* Devuelve 1 si hay ciclo negativo, 0 en caso contrario.
 * nxt[i][j] = siguiente vertice en el camino optimo de i a j. */
int floyd_warshall(int n, int W[][MAXV], int D[][MAXV],
                   int nxt[][MAXV], int verbose)
{
    int i, j, k;
    char titulo[32];

    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            D[i][j] = W[i][j];
            nxt[i][j] = (W[i][j] < INF && i != j) ? j : -1;
        }
        D[i][i] = 0;
        nxt[i][i] = i;
    }
    if (verbose) imprimir_matriz("D^(0):", n, D);

    for (k = 0; k < n; k++) {
        for (i = 0; i < n; i++) {
            for (j = 0; j < n; j++) {
                if (D[i][k] < INF && D[k][j] < INF &&
                    D[i][k] + D[k][j] < D[i][j]) {
                    D[i][j] = D[i][k] + D[k][j];
                    nxt[i][j] = nxt[i][k];
                }
            }
        }
        if (verbose) {
            sprintf(titulo, "D^(%d):", k + 1);
            imprimir_matriz(titulo, n, D);
        }
    }

    for (i = 0; i < n; i++)
        if (D[i][i] < 0) return 1;         /* ciclo de peso negativo */
    return 0;
}

void imprimir_camino(int u, int v, int D[][MAXV], int nxt[][MAXV])
{
    if (nxt[u][v] == -1) {
        printf("No existe camino de %d a %d\n", u + 1, v + 1);
        return;
    }
    printf("Camino %d -> %d (costo %d): %d", u + 1, v + 1, D[u][v], u + 1);
    while (u != v) {
        u = nxt[u][v];
        printf(" -> %d", u + 1);
    }
    printf("\n");
}

void probar_floyd(void)
{
    int n = 5, i, j;
    int W[MAXV][MAXV], D[MAXV][MAXV], nxt[MAXV][MAXV];

    for (i = 0; i < MAXV; i++)
        for (j = 0; j < MAXV; j++)
            W[i][j] = (i == j) ? 0 : INF;

    /* Grafo dirigido de 5 vertices con aristas negativas (sin ciclos neg.) */
    W[0][1] = 3;  W[0][2] = 8;  W[0][4] = -4;
    W[1][3] = 1;  W[1][4] = 7;
    W[2][1] = 4;
    W[3][0] = 2;  W[3][2] = -5;
    W[4][3] = 6;

    imprimir_matriz("Matriz de pesos W:", n, W);
    if (floyd_warshall(n, W, D, nxt, 1))
        printf("El grafo tiene un ciclo de peso negativo.\n");
    else
        imprimir_matriz("Matriz final de distancias minimas:", n, D);

    imprimir_camino(0, 2, D, nxt);
    imprimir_camino(3, 4, D, nxt);
}

/* ====================================================================
 * PROGRAMA PRINCIPAL
 * ==================================================================== */
int main(void)
{
    int p1[] = {30, 35, 15, 5, 10, 20, 25};   /* 6 matrices, optimo = 15125 */
    int p2[] = {10, 20, 30, 40, 30};          /* 4 matrices, optimo = 30000 */

    printf("=== 1. MULTIPLICACION DE CADENAS DE MATRICES ===\n");
    probar_mcm(p1, 6);
    probar_mcm(p2, 4);

    printf("=== 2. SUBSECUENCIA COMUN MAS LARGA ===\n");
    probar_lcs("ABCBDAB", "BDCABA");
    probar_lcs("AGGTAB", "GXTXAYB");

    printf("=== 3. FLOYD-WARSHALL ===\n");
    probar_floyd();

    return 0;
}