// hash_table.hpp - Tabla hash con encadenamiento separado (manejo de colisiones con listas)
// Verificar una palabra: O(1) promedio, O(n) peor caso (todas en la misma cubeta)
#pragma once
#include <string>
#include <vector>
#include <algorithm>

class TablaHash {
    struct Entrada {
        std::string clave;
        int freq;
    };
    std::vector<std::vector<Entrada>> cubetas;
    size_t n = 0;  // cantidad de elementos

    // Función hash djb2: h = h*33 + c
    static size_t funcionHash(const std::string& s) {
        size_t h = 5381;
        for (unsigned char c : s) h = h * 33 + c;
        return h;
    }

    // Duplica las cubetas y reubica todo (rehash) cuando el factor de carga supera 0.75
    void redimensionar() {
        std::vector<std::vector<Entrada>> nuevas(cubetas.size() * 2);
        for (auto& cubeta : cubetas)
            for (auto& e : cubeta) nuevas[funcionHash(e.clave) % nuevas.size()].push_back(e);
        cubetas.swap(nuevas);
    }

public:
    explicit TablaHash(size_t capacidad = 1024) : cubetas(capacidad) {}

    // Inserta (o actualiza) una clave. Devuelve true si era nueva. O(1) amortizado
    bool insertar(const std::string& clave, int freq) {
        if (static_cast<double>(n + 1) / cubetas.size() > 0.75) redimensionar();
        auto& cubeta = cubetas[funcionHash(clave) % cubetas.size()];
        for (auto& e : cubeta)
            if (e.clave == clave) { e.freq = freq; return false; }
        cubeta.push_back({clave, freq});
        ++n;
        return true;
    }

    // Devuelve la frecuencia de la palabra, o -1 si no existe. O(1) promedio
    int frecuencia(const std::string& clave) const {
        const auto& cubeta = cubetas[funcionHash(clave) % cubetas.size()];
        for (const auto& e : cubeta)
            if (e.clave == clave) return e.freq;
        return -1;
    }

    bool contiene(const std::string& clave) const { return frecuencia(clave) >= 0; }

    // Estadísticas para la exposición
    size_t tamano() const { return n; }
    size_t numCubetas() const { return cubetas.size(); }
    double factorCarga() const { return static_cast<double>(n) / cubetas.size(); }
    size_t cadenaMasLarga() const {
        size_t m = 0;
        for (const auto& c : cubetas) m = std::max(m, c.size());
        return m;
    }
    size_t cubetasVacias() const {
        size_t v = 0;
        for (const auto& c : cubetas) if (c.empty()) ++v;
        return v;
    }
};
