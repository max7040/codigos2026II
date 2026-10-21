// corrector.hpp - Sugerencias de corrección ortográfica.
// Recorre el diccionario, calcula la distancia de edición (programación dinámica) contra cada
// palabra candidata y se queda con las K mejores usando un heap.
// Mejor = menor distancia; a igual distancia, mayor frecuencia; luego orden alfabético.
#pragma once
#include <cstdlib>
#include <string>
#include <vector>
#include "utils.hpp"
#include "heap.hpp"
#include "edit_distance.hpp"

struct MejorCorreccion {
    bool operator()(const Sugerencia& a, const Sugerencia& b) const {
        if (a.distancia != b.distancia) return a.distancia < b.distancia;
        if (a.freq != b.freq) return a.freq > b.freq;
        return a.palabra < b.palabra;
    }
};

// Complejidad: O(N * m * L) con N palabras, longitud media L y palabra de longitud m;
// el filtro por longitud descarta casi todo el diccionario antes de calcular la distancia.
inline std::vector<Sugerencia> corregir(const std::string& palabra, const std::vector<Palabra>& dic,
                                        size_t k = 5, int distMax = 2) {
    TopK<Sugerencia, MejorCorreccion> top(k, MejorCorreccion());
    for (const Palabra& p : dic) {
        int difLong = std::abs(static_cast<int>(p.texto.size()) - static_cast<int>(palabra.size()));
        if (difLong > distMax) continue;                 // poda: no puede estar a distancia <= distMax
        int d = distanciaDP(palabra, p.texto);
        if (d <= distMax) top.insertar({p.texto, d, p.freq});
    }
    return top.resultado();
}
