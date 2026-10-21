// utils.hpp - Utilidades comunes: tipos, normalización de texto, carga del diccionario y cronómetro
#pragma once
#include <string>
#include <vector>
#include <fstream>
#include <chrono>
#include <cctype>

// Una entrada del diccionario: la palabra y su frecuencia de uso (simulada)
struct Palabra {
    std::string texto;
    int freq;
};

// Una sugerencia producida por el autocompletado o el corrector
struct Sugerencia {
    std::string palabra;
    int distancia;  // 0 en el autocompletado
    int freq;
};

// Convierte a minúsculas ASCII, quita tildes (á é í ó ú ü) y convierte ñ en n.
// Ignora cualquier carácter que no sea letra. Complejidad: O(n)
inline std::string normalizar(const std::string& s) {
    std::string out;
    for (size_t i = 0; i < s.size(); ++i) {
        unsigned char c = static_cast<unsigned char>(s[i]);
        if (c < 128) {
            if (std::isalpha(c)) out += static_cast<char>(std::tolower(c));
        } else if (c == 0xC3 && i + 1 < s.size()) {  // letras UTF-8 de dos bytes
            unsigned char d = static_cast<unsigned char>(s[++i]);
            switch (d) {
                case 0xA1: case 0x81: out += 'a'; break;
                case 0xA9: case 0x89: out += 'e'; break;
                case 0xAD: case 0x8D: out += 'i'; break;
                case 0xB3: case 0x93: out += 'o'; break;
                case 0xBA: case 0x9A: case 0xBC: case 0x9C: out += 'u'; break;
                case 0xB1: case 0x91: out += 'n'; break;
                default: break;
            }
        }
    }
    return out;
}

// Lee diccionario.txt (formato "palabra frecuencia" por línea). Devuelve vacío si no existe.
inline std::vector<Palabra> cargarDiccionario(const std::string& ruta) {
    std::vector<Palabra> dic;
    std::ifstream in(ruta);
    std::string w;
    int f;
    while (in >> w >> f) dic.push_back({w, f});
    return dic;
}

// Cronómetro simple basado en std::chrono
class Cronometro {
    std::chrono::high_resolution_clock::time_point t0;
public:
    Cronometro() { reiniciar(); }
    void reiniciar() { t0 = std::chrono::high_resolution_clock::now(); }
    double ms() const {  // milisegundos transcurridos
        return std::chrono::duration<double, std::milli>(
                   std::chrono::high_resolution_clock::now() - t0).count();
    }
};
