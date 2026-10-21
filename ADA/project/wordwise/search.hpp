// search.hpp - Búsqueda lineal y binaria sobre un vector de palabras.
//  Lineal:  O(n)       (no necesita orden)
//  Binaria: O(log n)   (requiere el vector ordenado)
// (La búsqueda con tabla hash es O(1) promedio y con Trie es O(m): ver hash_table.hpp y trie.hpp)
#pragma once
#include <string>
#include <vector>

inline int busquedaLineal(const std::vector<std::string>& v, const std::string& x) {
    for (size_t i = 0; i < v.size(); ++i)
        if (v[i] == x) return static_cast<int>(i);
    return -1;
}

inline int busquedaBinaria(const std::vector<std::string>& v, const std::string& x) {
    int lo = 0, hi = static_cast<int>(v.size()) - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (v[mid] == x) return mid;
        if (v[mid] < x) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
