#include <iostream>
#include <string>
using namespace std;

int main() {
    string numero;
    int baseOrigen, baseDestino;

    cout << "Ingrese el numero: ";
    cin >> numero;

    cout << "Ingrese la base de origen: ";
    cin >> baseOrigen;

    cout << "Ingrese la base de destino: ";
    cin >> baseDestino;

    int decimal = 0;

    for (char c : numero) {
        int digito;

        if (c >= '0' && c <= '9')
            digito = c - '0';
        else
            digito = c - 'A' + 10;

        // Validar digito
        if (digito >= baseOrigen) {
            cout << "Error: el digito " << c
                 << " no pertenece a la base "
                 << baseOrigen << endl;
            return 0;
        }

        decimal = decimal * baseOrigen + digito;
    }

    string resultado = "";

    if (decimal == 0) {
        resultado = "0";
    }

    while (decimal > 0) {
        int digito = decimal % baseDestino;

        if (digito < 10)
            resultado = char('0' + digito) + resultado;
        else
            resultado = char('A' + digito - 10) + resultado;

        decimal /= baseDestino;
    }

    cout << "Resultado: " << resultado << endl;

    return 0;
}