#include <iostream>
using namespace std;

void seleccion(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        int menor = i;

        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[menor]) {
                menor = j;
            }
        }

        swap(arr[i], arr[menor]);
    }
}

int main() {
    int arr[] = {5, 3, 8, 4, 2};
    int n = 5;

    seleccion(arr, n);

    for (int i = 0; i < n; i++)
        cout << arr[i] << " ";

    return 0;
}