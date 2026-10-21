// sorting.hpp - Algoritmos de ordenamiento genéricos (reciben un comparador cmp(a,b) = "a va antes que b")
//
//  Algoritmo                 Mejor        Promedio     Peor         Espacio
//  Burbuja (con bandera)     O(n)         O(n^2)       O(n^2)       O(1)
//  Inserción                 O(n)         O(n^2)       O(n^2)       O(1)
//  Selección                 O(n^2)       O(n^2)       O(n^2)       O(1)
//  Merge Sort                O(n log n)   O(n log n)   O(n log n)   O(n)
//  Quick Sort (mediana de 3) O(n log n)   O(n log n)   O(n^2)*      O(log n)
//  Quick Sort (pivote final) O(n log n)   O(n log n)   O(n^2)       O(n) en el peor caso
//  (*) con mediana de 3 el peor caso es muy difícil de provocar con datos reales
#pragma once
#include <vector>
#include <functional>
#include <utility>

// ---------- Algoritmos básicos O(n^2) ----------

template <class T, class Cmp = std::less<T>>
void burbuja(std::vector<T>& a, Cmp cmp = Cmp()) {
    int n = static_cast<int>(a.size());
    for (int i = 0; i < n - 1; ++i) {
        bool huboCambio = false;
        for (int j = 0; j < n - 1 - i; ++j)
            if (cmp(a[j + 1], a[j])) { std::swap(a[j], a[j + 1]); huboCambio = true; }
        if (!huboCambio) break;  // ya está ordenado: mejor caso O(n)
    }
}

template <class T, class Cmp = std::less<T>>
void insercion(std::vector<T>& a, Cmp cmp = Cmp()) {
    for (size_t i = 1; i < a.size(); ++i) {
        T clave = std::move(a[i]);
        int j = static_cast<int>(i) - 1;
        while (j >= 0 && cmp(clave, a[j])) { a[j + 1] = std::move(a[j]); --j; }
        a[j + 1] = std::move(clave);
    }
}

template <class T, class Cmp = std::less<T>>
void seleccion(std::vector<T>& a, Cmp cmp = Cmp()) {
    int n = static_cast<int>(a.size());
    for (int i = 0; i < n - 1; ++i) {
        int m = i;
        for (int j = i + 1; j < n; ++j)
            if (cmp(a[j], a[m])) m = j;
        if (m != i) std::swap(a[i], a[m]);
    }
}

// ---------- Divide y vencerás: Merge Sort ----------

template <class T, class Cmp>
void mezclar(std::vector<T>& a, std::vector<T>& tmp, int izq, int med, int der, Cmp cmp) {
    int i = izq, j = med + 1, k = izq;
    while (i <= med && j <= der)
        tmp[k++] = cmp(a[j], a[i]) ? std::move(a[j++]) : std::move(a[i++]);  // estable
    while (i <= med) tmp[k++] = std::move(a[i++]);
    while (j <= der) tmp[k++] = std::move(a[j++]);
    for (int x = izq; x <= der; ++x) a[x] = std::move(tmp[x]);
}

template <class T, class Cmp>
void mergeSortRec(std::vector<T>& a, std::vector<T>& tmp, int izq, int der, Cmp cmp) {
    if (izq >= der) return;                       // caso base
    int med = izq + (der - izq) / 2;
    mergeSortRec(a, tmp, izq, med, cmp);          // dividir
    mergeSortRec(a, tmp, med + 1, der, cmp);
    mezclar(a, tmp, izq, med, der, cmp);          // combinar: O(n)   =>   T(n) = 2T(n/2) + O(n)
}

template <class T, class Cmp = std::less<T>>
void mergeSort(std::vector<T>& a, Cmp cmp = Cmp()) {
    if (a.size() < 2) return;
    std::vector<T> tmp(a.size());
    mergeSortRec(a, tmp, 0, static_cast<int>(a.size()) - 1, cmp);
}

// ---------- Divide y vencerás: Quick Sort ----------

// Versión robusta: pivote = mediana de tres, partición de Hoare y recursión sólo sobre
// la parte más pequeña (profundidad máxima O(log n)).
template <class T, class Cmp>
void quickSortRec(std::vector<T>& a, int lo, int hi, Cmp cmp) {
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (cmp(a[mid], a[lo])) std::swap(a[mid], a[lo]);
        if (cmp(a[hi], a[lo])) std::swap(a[hi], a[lo]);
        if (cmp(a[hi], a[mid])) std::swap(a[hi], a[mid]);
        T pivote = a[mid];
        int i = lo, j = hi;
        while (i <= j) {
            while (cmp(a[i], pivote)) ++i;
            while (cmp(pivote, a[j])) --j;
            if (i <= j) { std::swap(a[i], a[j]); ++i; --j; }
        }
        if (j - lo < hi - i) { quickSortRec(a, lo, j, cmp); lo = i; }
        else                 { quickSortRec(a, i, hi, cmp); hi = j; }
    }
}

template <class T, class Cmp = std::less<T>>
void quickSort(std::vector<T>& a, Cmp cmp = Cmp()) {
    if (a.size() < 2) return;
    quickSortRec(a, 0, static_cast<int>(a.size()) - 1, cmp);
}

// Versión "ingenua": pivote = último elemento (Lomuto). Se incluye SOLO para mostrar el peor caso
// O(n^2) cuando la entrada ya está ordenada o invertida. Úsese con n pequeño.
template <class T, class Cmp>
void quickSortIngenuoRec(std::vector<T>& a, int lo, int hi, Cmp cmp) {
    if (lo >= hi) return;
    T pivote = a[hi];
    int i = lo - 1;
    for (int j = lo; j < hi; ++j)
        if (cmp(a[j], pivote)) std::swap(a[++i], a[j]);
    std::swap(a[i + 1], a[hi]);
    quickSortIngenuoRec(a, lo, i, cmp);
    quickSortIngenuoRec(a, i + 2, hi, cmp);
}

template <class T, class Cmp = std::less<T>>
void quickSortIngenuo(std::vector<T>& a, Cmp cmp = Cmp()) {
    if (a.size() < 2) return;
    quickSortIngenuoRec(a, 0, static_cast<int>(a.size()) - 1, cmp);
}
