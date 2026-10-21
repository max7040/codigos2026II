// trie.hpp - Árbol de prefijos (Trie) para autocompletado.
// Insertar / buscar una palabra de longitud m: O(m), independiente de cuántas palabras haya.
// Autocompletar: O(m + tamaño del subárbol del prefijo) y se queda con las K más frecuentes (heap).
#pragma once
#include <string>
#include <vector>
#include "utils.hpp"
#include "heap.hpp"

class Trie {
    struct Nodo {
        Nodo* hijos[26] = {};
        bool esFin = false;
        int freq = 0;
        ~Nodo() { for (Nodo* h : hijos) delete h; }
    };
    Nodo* raiz = new Nodo();
    size_t nodos = 1;

    // "a es mejor que b" en el autocompletado: más frecuente primero, desempate alfabético
    struct MejorFrecuencia {
        bool operator()(const Sugerencia& a, const Sugerencia& b) const {
            if (a.freq != b.freq) return a.freq > b.freq;
            return a.palabra < b.palabra;
        }
    };

    // Recorrido recursivo en profundidad (DFS) del subárbol que cuelga del prefijo
    void recolectar(const Nodo* nodo, std::string& actual, TopK<Sugerencia, MejorFrecuencia>& top) const {
        if (nodo->esFin) top.insertar({actual, 0, nodo->freq});
        for (int c = 0; c < 26; ++c) {
            if (nodo->hijos[c]) {
                actual.push_back(static_cast<char>('a' + c));
                recolectar(nodo->hijos[c], actual, top);
                actual.pop_back();  // retroceso
            }
        }
    }

    const Nodo* buscarNodo(const std::string& s) const {
        const Nodo* n = raiz;
        for (char ch : s) {
            if (ch < 'a' || ch > 'z') return nullptr;
            n = n->hijos[ch - 'a'];
            if (!n) return nullptr;
        }
        return n;
    }

public:
    Trie() = default;
    Trie(const Trie&) = delete;
    Trie& operator=(const Trie&) = delete;
    ~Trie() { delete raiz; }

    void insertar(const std::string& palabra, int freq) {
        Nodo* n = raiz;
        for (char ch : palabra) {
            if (ch < 'a' || ch > 'z') return;  // sólo letras a-z
            int i = ch - 'a';
            if (!n->hijos[i]) { n->hijos[i] = new Nodo(); ++nodos; }
            n = n->hijos[i];
        }
        n->esFin = true;
        n->freq = freq;
    }

    bool contiene(const std::string& palabra) const {
        const Nodo* n = buscarNodo(palabra);
        return n && n->esFin;
    }

    // Las k palabras más frecuentes que empiezan con 'prefijo'
    std::vector<Sugerencia> autocompletar(const std::string& prefijo, size_t k) const {
        const Nodo* n = buscarNodo(prefijo);
        if (!n) return {};
        TopK<Sugerencia, MejorFrecuencia> top(k, MejorFrecuencia());
        std::string actual = prefijo;
        recolectar(n, actual, top);
        return top.resultado();
    }

    size_t numNodos() const { return nodos; }
};
