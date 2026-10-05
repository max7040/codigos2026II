#include <iostream>
#include <cmath>
using namespace std;

double polinomio(double a[], int n, double x) {
    if (n == 0) {
        return a[0];
    }

    return a[n] * pow(x, n) + polinomio(a, n - 1, x);
}

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

    cout << "Resultado: "
         << polinomio(a, n, x) << endl;

    return 0;
}