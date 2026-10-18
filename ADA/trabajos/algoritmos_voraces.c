#include <stdio.h>

#define MAX 100
#define INF 1000000000

/* 1. Ordenamiento voraz: Selection Sort */
void ordenar(void) {
    int n, a[MAX];

    printf("Cantidad de numeros (1-%d): ", MAX);
    if (scanf("%d", &n) != 1 || n < 1 || n > MAX) {
        printf("Cantidad no valida.\n");
        return;
    }

    for (int i = 0; i < n; i++) {
        printf("Numero %d: ", i + 1);
        scanf("%d", &a[i]);
    }

    for (int i = 0; i < n - 1; i++) {
        int menor = i;
        for (int j = i + 1; j < n; j++) {
            if (a[j] < a[menor]) {
                menor = j;
            }
        }
        int temp = a[i];
        a[i] = a[menor];
        a[menor] = temp;
    }

    printf("Numeros ordenados: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", a[i]);
    }
    printf("\n");
}

/* 2. Camino mas corto: algoritmo de Dijkstra */
void dijkstra(void) {
    int n, origen;
    int grafo[MAX][MAX], dist[MAX], visitado[MAX] = {0};

    printf("Cantidad de vertices (1-%d): ", MAX);
    if (scanf("%d", &n) != 1 || n < 1 || n > MAX) {
        printf("Cantidad no valida.\n");
        return;
    }

    printf("Ingrese la matriz de adyacencia (%d x %d).\n", n, n);
    printf("Use 0 si no existe una arista y pesos no negativos.\n");
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            scanf("%d", &grafo[i][j]);
            if (grafo[i][j] < 0) {
                printf("Dijkstra no admite pesos negativos.\n");
                return;
            }
        }
    }

    printf("Vertice de origen (1-%d): ", n);
    if (scanf("%d", &origen) != 1 || origen < 1 || origen > n) {
        printf("Origen no valido.\n");
        return;
    }
    origen--;

    for (int i = 0; i < n; i++) {
        dist[i] = INF;
    }
    dist[origen] = 0;

    for (int paso = 0; paso < n; paso++) {
        int u = -1;
        for (int i = 0; i < n; i++) {
            if (!visitado[i] && (u == -1 || dist[i] < dist[u])) {
                u = i;
            }
        }

        if (u == -1 || dist[u] == INF) {
            break;
        }

        visitado[u] = 1;
        for (int v = 0; v < n; v++) {
            if (grafo[u][v] > 0 && !visitado[v] &&
                dist[u] + grafo[u][v] < dist[v]) {
                dist[v] = dist[u] + grafo[u][v];
            }
        }
    }

    printf("Distancias minimas desde el vertice %d:\n", origen + 1);
    for (int i = 0; i < n; i++) {
        if (dist[i] == INF) {
            printf("Hasta %d: no existe camino\n", i + 1);
        } else {
            printf("Hasta %d: %d\n", i + 1, dist[i]);
        }
    }
}

/* 3. Mochila fraccionaria: elegir por mayor valor/peso */
typedef struct {
    double peso;
    double valor;
    double razon;
} Objeto;

void mochila(void) {
    int n;
    double capacidad, pesoTotal = 0.0, valorTotal = 0.0;
    Objeto objetos[MAX];

    printf("Cantidad de objetos (1-%d): ", MAX);
    if (scanf("%d", &n) != 1 || n < 1 || n > MAX) {
        printf("Cantidad no valida.\n");
        return;
    }

    for (int i = 0; i < n; i++) {
        printf("Peso y valor del objeto %d: ", i + 1);
        if (scanf("%lf %lf", &objetos[i].peso, &objetos[i].valor) != 2 ||
            objetos[i].peso <= 0 || objetos[i].valor < 0) {
            printf("Peso o valor no valido.\n");
            return;
        }
        objetos[i].razon = objetos[i].valor / objetos[i].peso;
    }

    printf("Capacidad de la mochila: ");
    if (scanf("%lf", &capacidad) != 1 || capacidad < 0) {
        printf("Capacidad no valida.\n");
        return;
    }

    /* Ordenar por razon valor/peso descendente */
    for (int i = 0; i < n - 1; i++) {
        int mejor = i;
        for (int j = i + 1; j < n; j++) {
            if (objetos[j].razon > objetos[mejor].razon) {
                mejor = j;
            }
        }
        Objeto temp = objetos[i];
        objetos[i] = objetos[mejor];
        objetos[mejor] = temp;
    }

    for (int i = 0; i < n && pesoTotal < capacidad; i++) {
        double disponible = capacidad - pesoTotal;
        if (objetos[i].peso <= disponible) {
            pesoTotal += objetos[i].peso;
            valorTotal += objetos[i].valor;
        } else {
            double fraccion = disponible / objetos[i].peso;
            pesoTotal += disponible;
            valorTotal += objetos[i].valor * fraccion;
        }
    }

    printf("Peso utilizado: %.2f\n", pesoTotal);
    printf("Valor maximo aproximado: %.2f\n", valorTotal);
}

int main(void) {
    int opcion;

    do {
        printf("\n=== ALGORITMOS VORACES ===\n");
        printf("1. Ordenamiento (Selection Sort)\n");
        printf("2. Camino mas corto (Dijkstra)\n");
        printf("3. Mochila fraccionaria\n");
        printf("0. Salir\n");
        printf("Seleccione una opcion: ");

        if (scanf("%d", &opcion) != 1) {
            printf("Entrada no valida.\n");
            return 1;
        }

        switch (opcion) {
            case 1: ordenar(); break;
            case 2: dijkstra(); break;
            case 3: mochila(); break;
            case 0: printf("Programa finalizado.\n"); break;
            default: printf("Opcion no valida.\n");
        }
    } while (opcion != 0);

    return 0;
}
