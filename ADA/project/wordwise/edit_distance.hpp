// edit_distance.hpp - Distancia de edición (Levenshtein): mínimo de inserciones, borrados y
// sustituciones para convertir la palabra a en la palabra b.
//
//  - Versión recursiva pura: resuelve los mismos subproblemas una y otra vez -> crece como
//    el número de Delannoy (aprox. 3^n): exponencial.
//  - Programación dinámica: guarda cada subproblema en una tabla -> O(n*m) tiempo.
#pragma once
#include <string>
#include <vector>
#include <algorithm>

inline long long g_llamadasRecursivas = 0;  // contador para mostrar el costo en la exposición

// ---- Versión 1: recursión pura (exponencial) ----
inline int distanciaRecursiva(const std::string& a, const std::string& b, size_t i, size_t j) {
    ++g_llamadasRecursivas;
    if (i == 0) return static_cast<int>(j);  // insertar los j caracteres restantes de b
    if (j == 0) return static_cast<int>(i);  // borrar los i caracteres restantes de a
    int costo = (a[i - 1] == b[j - 1]) ? 0 : 1;
    return std::min({distanciaRecursiva(a, b, i - 1, j) + 1,           // borrar
                     distanciaRecursiva(a, b, i, j - 1) + 1,           // insertar
                     distanciaRecursiva(a, b, i - 1, j - 1) + costo}); // sustituir / coincidir
}

inline int distanciaRecursiva(const std::string& a, const std::string& b) {
    return distanciaRecursiva(a, b, a.size(), b.size());
}

// ---- Versión 2: programación dinámica, tabla completa (sirve para mostrar la matriz) ----
inline std::vector<std::vector<int>> matrizDistancia(const std::string& a, const std::string& b) {
    size_t n = a.size(), m = b.size();
    std::vector<std::vector<int>> d(n + 1, std::vector<int>(m + 1, 0));
    for (size_t i = 0; i <= n; ++i) d[i][0] = static_cast<int>(i);
    for (size_t j = 0; j <= m; ++j) d[0][j] = static_cast<int>(j);
    for (size_t i = 1; i <= n; ++i)
        for (size_t j = 1; j <= m; ++j) {
            int costo = (a[i - 1] == b[j - 1]) ? 0 : 1;
            d[i][j] = std::min({d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + costo});
        }
    return d;
}

// ---- Versión 3: programación dinámica optimizada en memoria (dos filas): tiempo O(n*m), espacio O(m) ----
inline int distanciaDP(const std::string& a, const std::string& b) {
    size_t n = a.size(), m = b.size();
    std::vector<int> prev(m + 1), cur(m + 1);
    for (size_t j = 0; j <= m; ++j) prev[j] = static_cast<int>(j);
    for (size_t i = 1; i <= n; ++i) {
        cur[0] = static_cast<int>(i);
        for (size_t j = 1; j <= m; ++j) {
            int costo = (a[i - 1] == b[j - 1]) ? 0 : 1;
            cur[j] = std::min({prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + costo});
        }
        prev.swap(cur);
    }
    return prev[m];
}
