#include <iostream>
using namespace std;

int main() {
    int n;
    double x;

    cout << "Grado del polinomio: ";
    cin >> n;

    double a[n + 1];

    cout << "Ingrese los coeficientes:\n";
    for (int i = 0; i <= n; i++) {
        cin >> a[i];
    }

    cout << "Ingrese x: ";
    cin >> x;

    double resultado = 0;

    for (int i = 0; i <= n; i++) {
        double potencia = 1;

        for (int j = 0; j < i; j++) {
            potencia *= x;
        }

        resultado += a[i] * potencia;
    }

    cout << "Resultado: " << resultado << endl;

    return 0;
}