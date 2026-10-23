
#pragma once
#include <cstdio>
#include <random>
#include <functional>
#include <algorithm>
#include <string>
#include <vector>
#include <fstream>
#include "utils.hpp"
#include "sorting.hpp"
#include "search.hpp"
#include "hash_table.hpp"
#include "trie.hpp"
#include "edit_distance.hpp"

using Datos = std::vector<std::string>;

// Genera n palabras tomadas al azar (con repetición) del diccionario. Semilla fija = resultados repetibles.
inline Datos generarDatos(const std::vector<Palabra>& dic, int n, unsigned semilla = 42) {
    std::mt19937 rng(semilla);
    std::uniform_int_distribution<size_t> dist(0, dic.size() - 1);
    Datos v;
    v.reserve(n);
    for (int i = 0; i < n; ++i) v.push_back(dic[dist(rng)].texto);
    return v;
}

// Tiempo promedio (ms) de aplicar 'f' sobre una copia de 'base'. Verifica que el resultado quede ordenado.
inline double medirOrdenamiento(const std::function<void(Datos&)>& f, const Datos& base, int reps, bool& ok) {
    double total = 0;
    for (int r = 0; r < reps; ++r) {
        Datos trabajo = base;  // la copia no se cuenta en el tiempo
        Cronometro c;
        f(trabajo);
        total += c.ms();
        if (!std::is_sorted(trabajo.begin(), trabajo.end())) ok = false;
    }
    return total / reps;
}

inline void benchmarkOrdenamiento(const std::vector<Palabra>& dic, bool completo, std::ofstream& csv) {
    struct Algoritmo {
        std::string nombre;
        std::function<void(Datos&)> f;
        int limiteN;  // tamaño máximo con el que se ejecuta (los O(n^2) son lentísimos con n grande)
    };
    const int SIN_LIMITE = 1 << 30;
    const int LIM2 = completo ? SIN_LIMITE : 10000;
    std::vector<Algoritmo> algos = {
        {"Burbuja            O(n^2)", [](Datos& v) { burbuja(v); }, LIM2},
        {"Insercion          O(n^2)", [](Datos& v) { insercion(v); }, LIM2},
        {"Seleccion          O(n^2)", [](Datos& v) { seleccion(v); }, LIM2},
        {"QuickSort pivote final", [](Datos& v) { quickSortIngenuo(v); }, 10000},  // peor caso O(n^2) + recursión profunda
        {"Merge Sort     O(n log n)", [](Datos& v) { mergeSort(v); }, SIN_LIMITE},
        {"Quick Sort med3 O(nlog n)", [](Datos& v) { quickSort(v); }, SIN_LIMITE},
        {"std::sort (referencia)", [](Datos& v) { std::sort(v.begin(), v.end()); }, SIN_LIMITE},
    };
    const std::vector<int> tamanos = {1000, 5000, 10000, 50000, 100000};
    const char* nombresCaso[3] = {"ALEATORIA", "YA ORDENADA", "INVERSA"};
    bool todoOk = true;

    std::printf("\n=== BENCHMARK DE ORDENAMIENTO (tiempo promedio en milisegundos) ===\n");
    for (int caso = 0; caso < 3; ++caso) {
        std::printf("\n--- Caso: %s ---\n%-28s", nombresCaso[caso], "Algoritmo \\ n");
        for (int n : tamanos) std::printf("%11d", n);
        std::printf("\n");

        // Se prepara el conjunto de datos de cada tamaño para este caso
        std::vector<Datos> bases;
        for (int n : tamanos) {
            Datos d = generarDatos(dic, n);
            if (caso >= 1) std::sort(d.begin(), d.end());
            if (caso == 2) std::reverse(d.begin(), d.end());
            bases.push_back(std::move(d));
        }
        for (const Algoritmo& a : algos) {
            std::printf("%-28s", a.nombre.c_str());
            for (size_t k = 0; k < tamanos.size(); ++k) {
                int n = tamanos[k];
                if (n > a.limiteN) { std::printf("%11s", "--"); continue; }
                int reps = (n > 10000 && a.limiteN < SIN_LIMITE) ? 1 : (n <= 10000 ? 5 : 3);
                bool ok = true;
                double ms = medirOrdenamiento(a.f, bases[k], reps, ok);
                if (!ok) todoOk = false;
                std::printf("%11.3f", ms);
                std::fflush(stdout);
                csv << "ordenamiento," << a.nombre << "," << nombresCaso[caso] << "," << n << "," << ms << "\n";
            }
            std::printf("\n");
        }
    }
    if (!completo) std::printf("\n('--' = no se ejecuta por ser demasiado lento; use el modo completo para incluirlo)\n");
    std::printf("Verificacion de orden correcto en todas las corridas: %s\n", todoOk ? "OK" : "ERROR");
}

inline void benchmarkDistancia(std::ofstream& csv) {
    std::printf("\n=== DISTANCIA DE EDICION: recursiva pura vs programacion dinamica ===\n");
    std::printf("(dos palabras totalmente distintas = peor caso de la recursion)\n\n");
    std::printf("%8s %16s %16s %14s %12s\n", "longitud", "llamadas rec.", "recursiva (ms)", "DP (ms)", "veces mas");
    const std::string A = "abcdefghijkl", B = "mnopqrstuvwx";
    for (int len : {4, 6, 8, 10, 12}) {
        std::string a = A.substr(0, len), b = B.substr(0, len);

        g_llamadasRecursivas = 0;
        Cronometro c1;
        int r1 = distanciaRecursiva(a, b);
        double msRec = c1.ms();
        long long llamadas = g_llamadasRecursivas;

        const int REPS = 2000;
        volatile int sink = 0;
        Cronometro c2;
        for (int i = 0; i < REPS; ++i) sink = sink + distanciaDP(a, b);
        double msDP = c2.ms() / REPS;
        int r2 = distanciaDP(a, b);

        std::printf("%8d %16lld %16.4f %14.5f %11.0fx%s\n", len, llamadas, msRec, msDP,
                    msDP > 0 ? msRec / msDP : 0.0, r1 == r2 ? "" : "  ERROR");
        csv << "distancia,recursiva,peor_caso," << len << "," << msRec << "\n";
        csv << "distancia,programacion_dinamica,peor_caso," << len << "," << msDP << "\n";
    }
}

inline void benchmarkBusqueda(const std::vector<Palabra>& dic, std::ofstream& csv) {
    // Estructuras construidas a partir del diccionario
    Datos ordenadas;
    TablaHash tabla;
    Trie trie;
    for (const Palabra& p : dic) {
        ordenadas.push_back(p.texto);
        tabla.insertar(p.texto, p.freq);
        trie.insertar(p.texto, p.freq);
    }
    mergeSort(ordenadas);  // necesario para la búsqueda binaria

    // 20 000 consultas: la mitad existen y la otra mitad no (se les añade una 'x' al final)
    const int Q = 20000;
    Datos consultas = generarDatos(dic, Q, 7);
    for (int i = 0; i < Q; i += 2) consultas[i] += "x";

    struct Metodo { std::string nombre; std::function<bool(const std::string&)> f; };
    std::vector<Metodo> metodos = {
        {"Busqueda lineal   O(n)", [&](const std::string& s) { return busquedaLineal(ordenadas, s) >= 0; }},
        {"Busqueda binaria  O(log n)", [&](const std::string& s) { return busquedaBinaria(ordenadas, s) >= 0; }},
        {"Tabla hash        O(1)", [&](const std::string& s) { return tabla.contiene(s); }},
        {"Trie              O(m)", [&](const std::string& s) { return trie.contiene(s); }},
    };

    std::printf("\n=== BUSQUEDA: %d consultas sobre %zu palabras (50%% existen, 50%% no) ===\n\n", Q, dic.size());
    std::printf("%-30s %14s %18s %10s\n", "Metodo", "total (ms)", "por consulta (us)", "halladas");
    for (const Metodo& m : metodos) {
        const int REPS = 3;
        double total = 0;
        int halladas = 0;
        for (int r = 0; r < REPS; ++r) {
            halladas = 0;
            Cronometro c;
            for (const std::string& q : consultas) halladas += m.f(q) ? 1 : 0;
            total += c.ms();
        }
        double ms = total / REPS;
        std::printf("%-30s %14.3f %18.4f %10d\n", m.nombre.c_str(), ms, ms * 1000.0 / Q, halladas);
        csv << "busqueda," << m.nombre << ",50pct_existen," << Q << "," << ms << "\n";
    }
}
