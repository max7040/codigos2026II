#include <iostream>
using namespace std;

int particion(int arr[], int inicio, int fin) {
    int pivote = arr[fin];
    int i = inicio - 1;

    for (int j = inicio; j < fin; j++) {
        if (arr[j] < pivote) {
            i++;
            swap(arr[i], arr[j]);
        }
    }

    swap(arr[i + 1], arr[fin]);

    return i + 1;
}

void quickSort(int arr[], int inicio, int fin) {
    if (inicio < fin) {
        int p = particion(arr, inicio, fin);

        quickSort(arr, inicio, p - 1);
        quickSort(arr, p + 1, fin);
    }
}

int main() {
    int arr[] = {5, 3, 8, 4, 2};
    int n = 5;

    quickSort(arr, 0, n - 1);

    for (int i = 0; i < n; i++)
        cout << arr[i] << " ";

    return 0;
}