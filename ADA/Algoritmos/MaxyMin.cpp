#include <iostream>
#include <vector>
#include <climits>

using namespace std;

int n;
vector<vector<int>> grafo;
vector<bool> visitado;

int costoMinimo = INT_MAX;
int costoMaximo = INT_MIN;

vector<int> caminoActual;
vector<int> caminoMinimo;
vector<int> caminoMaximo;

void buscarCaminos(int actual, int destino, int costoActual) {

    if (actual == destino) {


        if (costoActual < costoMinimo) {
            costoMinimo = costoActual;
            caminoMinimo = caminoActual;
        }

        if (costoActual > costoMaximo) {
            costoMaximo = costoActual;
            caminoMaximo = caminoActual;
        }

        return;
    }

    // Probar todos los nodos
    for (int siguiente = 1; siguiente <= n; siguiente++) {

        if (grafo[actual][siguiente] != 0 &&
            !visitado[siguiente]) {

            visitado[siguiente] = true;
            caminoActual.push_back(siguiente);

            buscarCaminos(
                siguiente,
                destino,
                costoActual + grafo[actual][siguiente]
            );

            caminoActual.pop_back();// retrocedemos para probar otra conexxion
            visitado[siguiente] = false;
        }
    }
}

void mostrarCamino(const vector<int>& camino) {

    for (int i = 0; i < camino.size(); i++) {

        cout << camino[i];

        if (i < camino.size() - 1)
            cout << " -> ";
    }

    cout << endl;
}

int main() {

    int conexiones;

    cout << "Ingrese cantidad de nodos: ";
    cin >> n;

    grafo.resize(n + 1, vector<int>(n + 1, 0));

    cout << "Ingrese cantidad de conexiones: ";
    cin >> conexiones;

    cout << "\nIngrese cada conexion:\n";
    cout << "Formato: origen destino costo\n\n";

    for (int i = 0; i < conexiones; i++) {

        int origen, destino, costo;

        cout << "Conexion " << i + 1 << ": ";
        cin >> origen >> destino >> costo;

        
        grafo[origen][destino] = costo;
        grafo[destino][origen] = costo;
    }

    
    int inicio, destino;

    cout << "\nIngrese nodo inicial: ";
    cin >> inicio;

    cout << "Ingrese nodo final: ";
    cin >> destino;

    
    visitado.resize(n + 1, false);

    visitado[inicio] = true;
    caminoActual.push_back(inicio);

    
    buscarCaminos(inicio, destino, 0);

    cout << "             RESULTADOS\n";

    if (costoMinimo == INT_MAX) {

        cout << "No existe un camino entre "
             << inicio << " y " << destino << ".\n";

    } else {

        cout << "\nCAMINO DE COSTO MINIMO:\n";
        mostrarCamino(caminoMinimo);

        cout << "Costo minimo: "
             << costoMinimo << endl;

        cout << "\nCAMINO DE COSTO MAXIMO:\n";
        mostrarCamino(caminoMaximo);

        cout << "Costo maximo: "
             << costoMaximo << endl;
    }

    return 0;
}