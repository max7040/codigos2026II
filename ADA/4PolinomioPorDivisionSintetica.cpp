#include <iostream>
using namespace std;

double divisionSintetica(double a[], int n, double x) {
    double resultado = a[0];

    for (int i = 1; i <= n; i++) {
        resultado = resultado * x + a[i];
    }

    return resultado;
}

int main() {
    int n;
    double x;

    cout << "Grado del polinomio: ";
    cin >> n;

    double a[n + 1];

    cout << "Ingrese los coeficientes desde el mayor grado:\n";

    for (int i = 0; i <= n; i++) {
        cin >> a[i];
    }

    cout << "Ingrese x: ";
    cin >> x;

    double resultado = divisionSintetica(a, n, x);

    cout << "Resultado: " << resultado << endl;

    return 0;
}