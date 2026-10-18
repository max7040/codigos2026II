#include <iostream>
using namespace std;

void merge(int arr[], int inicio, int medio, int fin) {
    int i = inicio;
    int j = medio + 1;
    int k = 0;

    int temp[100];

    while (i <= medio && j <= fin) {
        if (arr[i] < arr[j])
            temp[k++] = arr[i++];
        else
            temp[k++] = arr[j++];
    }

    while (i <= medio)
        temp[k++] = arr[i++];

    while (j <= fin)
        temp[k++] = arr[j++];

    for (i = inicio, k = 0; i <= fin; i++, k++)
        arr[i] = temp[k];
}

void mergeSort(int arr[], int inicio, int fin) {
    if (inicio < fin) {
        int medio = (inicio + fin) / 2;

        mergeSort(arr, inicio, medio);
        mergeSort(arr, medio + 1, fin);

        merge(arr, inicio, medio, fin);
    }
}

int main() {
    int arr[] = {5, 3, 8, 4, 2};
    int n = 5;

    mergeSort(arr, 0, n - 1);

    for (int i = 0; i < n; i++)
        cout << arr[i] << " ";

    return 0;
}