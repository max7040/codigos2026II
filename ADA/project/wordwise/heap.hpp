// heap.hpp - Cola de prioridad (heap binario) usada para quedarse con las K mejores sugerencias.
// Se guarda un heap de tamaño máximo K cuya RAÍZ es la peor de las elegidas.
// Cada candidato nuevo se compara sólo con la raíz: O(log K) por candidato,
// total O(N log K) en vez de ordenar los N candidatos (O(N log N)).
#pragma once
#include <vector>
#include "sorting.hpp"

template <class T, class Mejor>  // Mejor(a,b) = true si a es mejor que b
class TopK {
    std::vector<T> h;
    size_t k;
    Mejor mejor;

    void subir(size_t i) {
        while (i > 0) {
            size_t p = (i - 1) / 2;
            if (mejor(h[p], h[i])) { std::swap(h[p], h[i]); i = p; }  // el padre debe ser el peor
            else break;
        }
    }
    void bajar(size_t i) {
        for (;;) {
            size_t l = 2 * i + 1, r = l + 1, c = i;
            // c = hijo "peor" entre los dos (si es peor que h[i], se intercambia)
            if (l < h.size() && mejor(h[c], h[l])) c = l;
            if (r < h.size() && mejor(h[c], h[r])) c = r;
            if (c == i) break;
            std::swap(h[i], h[c]);
            i = c;
        }
    }

public:
    TopK(size_t k_, Mejor m) : k(k_), mejor(m) {}

    void insertar(const T& x) {
        if (h.size() < k) { h.push_back(x); subir(h.size() - 1); }
        else if (!h.empty() && mejor(x, h[0])) { h[0] = x; bajar(0); }  // reemplaza a la peor
    }

    // Devuelve los K elegidos ordenados del mejor al peor (usa nuestro Merge Sort)
    std::vector<T> resultado() const {
        std::vector<T> v = h;
        mergeSort(v, mejor);
        return v;
    }
};
